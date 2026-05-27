from fastkml import kml

with open('test.kml', 'rb') as f:
    content = f.read()

k = kml.KML.from_string(content)

print("Type of k:", type(k))
print("k.features type:", type(k.features))
try:
    print("k.features:", list(k.features))
except Exception as e:
    print("Failed to list k.features:", e)
