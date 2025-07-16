resource "aws_instance" "test_ec2" {
  ami           = "ami-0c02fb55956c7d316" # Amazon Linux 2
  instance_type = "t2.micro"
  tags = {
    Name = "IdleTestInstance"
  }

  lifecycle {
    prevent_destroy = true
  }
}

resource "aws_ebs_volume" "idle_volume" {
  availability_zone = "us-east-1a"
  size              = 1
  tags = {
    Name = "IdleVolume"
  }
}

resource "aws_s3_bucket" "idle_bucket" {
  bucket = "idle-resources-demo-${random_id.bucket_id.hex}"
}

resource "random_id" "bucket_id" {
  byte_length = 4
}

resource "aws_eip" "idle_eip" {
  tags = {
    Name = "IdleEIP"
  }
}
