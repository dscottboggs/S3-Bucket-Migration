from functools import cached_property
from pathlib import Path
from yaml import safe_load as load
from minio import Minio
from minio.error import S3Error
from minio.datatypes import Object, Bucket
from typing import *


def io_copy(f, t, bufsize=0x1000, buffer=None):
    """Copy from `f` to `t`, `bufsize` bytes at a time"""
    buffer = buffer or bytearray(bufsize)
    while n := f.readinto(buffer):
        t.write(buffer[:n])


class Copier:
    """Hold two S3 connections for copying between them"""

    def __init__(self, from_config, from_conn, to_config, to_conn):
        self.from_conn = from_conn
        self.from_config = from_config
        self.to_conn = to_conn
        self.to_config = to_config

    def test_connections(self):
        """Test the connection to the configured minio instance."""
        assert self.from_conn.bucket_exists(
            self.from_config['bucket']), f"bucket {self.from_config['bucket']} does not exist"
        assert self.to_conn.bucket_exists(
            self.to_config['bucket']), f"bucket {self.to_config['bucket']} does not exist"

    @classmethod
    def load_config(cls) -> 'Copier':
        """Return the loaded config as a dict"""
        with open("access.yml") as file:
            config = load(file)
        return cls(
            config['from'],
            Minio(
                endpoint=config['from']['endpoint'],
                access_key=config['from']['access_key'],
                secret_key=config['from']['secret_key']
            ),
            config['to'],
            Minio(
                endpoint=config['to']['endpoint'],
                access_key=config['to']['access_key'],
                secret_key=config['to']['secret_key']
            )
        )

    def iter(self):
        return (
            (self.from_config, self.from_conn),
            (self.to_config, self.to_conn)
        )

    def list_from_files(self) -> Iterator[Object]:
        """Return a list of the files in the configured bucket from the "from" connection."""
        return self.from_conn.list_objects(self.from_config['bucket'], recursive=True)

    @cached_property
    def from_bucket(self) -> Bucket:
        self.from_conn.get_bucket(self.from_config['bucket'])

    @cached_property
    def to_bucket(self) -> Bucket:
        self.to_conn.get_bucket(self.to_config['bucket'])

    def do_migration(self):
        """Copy all of the files from the source bucket ("from") to the destination ("to")."""
        try:
            with open("completed.txt") as progress_log:
                completed = progress_log.readlines()
        except OSError:
            completed = []
        with open("completed.txt", mode="a") as progress_log:
            for obj in self.list_from_files():
                name = obj.object_name
                if name in completed:
                    continue
                try:
                    source = self.from_conn.get_object(
                        self.from_config['bucket'], name)
                    self.to_conn.put_object(self.to_config['bucket'],
                                            name,
                                            source,
                                            length=obj.size,
                                            content_type=obj.content_type,
                                            metadata=obj.metadata)
                finally:
                    source.close()
                    source.release_conn()
                progress_log.write(name + "\n")
                progress_log.flush()


def main():
    configs = Copier.load_config()
    configs.test_connections()
    configs.do_migration()


if __name__ == '__main__':
    main()
