import uuid

# Generate a random JWT secret key
JWT_SECRET = uuid.uuid4().hex

print("Generated JWT Secret:", JWT_SECRET)
