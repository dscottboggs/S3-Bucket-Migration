# S3 Bucket migration

This is a bit of a quick-n-dirty script for copying all files from one S3
bucket to another. It is intended to work across multiple providers &mdash; it
was originally written to migrate data stored in Minio to Backblaze.

The "quick-n-dirty" aspect comes from the fact that this script doesn't do
any sort of parallelism, so it's pretty slow. I have more than 177k files
taking up a little more than 25GiB and it looks like it's going to take around
14 uninterrupted hours. Someone who has more files than that could modify this
to make it more concurrent (and faster), but I don't think I'll need to for my
purposes.

## Usage
1. Clone this repo and `cd` into it
   ~~~console
   git clone git@github.com:dscottboggs/S3-Bucket-Migration.git
   cd S3-Bucket-Migration
   ~~~

2. create an `access.yml` file like this:
   ```yml
   from:
     endpoint: url of source server
     access_key: access key ID
     secret_key: secret key
     bucket: bucket name
   to:
     endpoint: url of destination server
     access_key: access key ID
     secret_key: secret key
     bucket: bucket name
   ```

3. Install the dependencies
   ~~~console
   python3 -m pip install -r requirements.txt
   ~~~

4. Run the script
   ~~~
   python s3_migrate.py
   ~~~

## Contributing
1. [Fork this repository](https://github.com/dscottboggs/S3-Bucket-Migration)
2. Clone your fork
3. Create a new branch
   ~~~console
   git checkout -b feature/my-new-feature
   ~~~
4. Make and commit your changes
   ~~~console
   git commit -am
   ~~~
5. Push your changes to your fork
   ~~~console
   git push -u origin feature/my-new-feature
   ~~~
6. Follow the link in the terminal output to create a pull request.
