#!/bin/bash

# Set output filenames
PRIVATE_KEY_PEM="private_key.pem"
PRIVATE_KEY_DER="private_key.der"
PUBLIC_KEY_PEM="public_key.pem"

echo "Generating 2048-bit RSA private key..."
openssl genrsa -out $PRIVATE_KEY_PEM 2048

echo "Converting to unencrypted PKCS#8 DER format..."
openssl pkcs8 -topk8 -inform PEM -outform DER -in $PRIVATE_KEY_PEM -out $PRIVATE_KEY_DER -nocrypt

echo "Generating public key (PEM format)..."
openssl rsa -in $PRIVATE_KEY_PEM -pubout -out $PUBLIC_KEY_PEM

echo ""
echo "All keys generated:"
echo "   • Private key PEM:  $PRIVATE_KEY_PEM"
echo "   • Private key DER:  $PRIVATE_KEY_DER"
echo "   • Public key PEM:   $PUBLIC_KEY_PEM"

echo ""
echo "Next steps:"
echo "1. Upload your public key to Snowflake (SQL):"
echo "---------------------------------------------"
echo "ALTER USER your_username SET RSA_PUBLIC_KEY='"
cat $PUBLIC_KEY_PEM
echo "';"
echo "---------------------------------------------"

echo ""
echo "2. Add this to your .env file:"
echo "---------------------------------------------"
echo "user=your_snowflake_username"
echo "account=your_snowflake_account"
echo "private_key_path=$(pwd)/$PRIVATE_KEY_DER"
echo "---------------------------------------------"

echo ""
echo "3. Use the DER key in your Python script as a byte file."
