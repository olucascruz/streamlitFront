from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
import os

def generate_key_pair():
    private_key = ec.generate_private_key(ec.SECP256R1(), default_backend())
    public_key = private_key.public_key()
    return private_key, public_key

def serialize_public_key(public_key):
    return public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )

def serialize_private_key(public_key):
    return public_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption()
    )

def derive_shared_key(private_key, public_key):
    return private_key.exchange(ec.ECDH(), public_key)

def derive_symmetric_key(shared_key, salt):
    return HKDF(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        info=b'',
        backend=default_backend()
    ).derive(shared_key)

def encrypt_message(key, iv, message):
    cipher = Cipher(algorithms.AES(key), modes.CFB(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    ciphertext = encryptor.update(message) + encryptor.finalize()
    return ciphertext

def decrypt_message(key, iv, ciphertext):
    cipher = Cipher(algorithms.AES(key), modes.CFB(iv), backend=default_backend())
    decryptor = cipher.decryptor()
    decrypted_message = decryptor.update(ciphertext) + decryptor.finalize()
    return decrypted_message

def main():

    #-------------------------------------------------------------
    #   CRIAÇÃO DAS CONTAS - GERANDO OS PARES DE CHAVES
    #-------------------------------------------------------------  

    # Remetente gera chaves
    private_key_sender, public_key_sender = generate_key_pair()
    public_key_sender_bytes = serialize_public_key(public_key_sender)
    # REMETENDE ENVIA CHAVE PUBLICA NO FORMATO .PEM PARA O SERVIDOR

    # Destinatário gera chaves
    private_key_receiver, public_key_receiver = generate_key_pair()
    public_key_receiver_bytes = serialize_public_key(public_key_receiver)
    # DESTINATARIO ENVIA CHAVE PUBLICA NO FORMATO .PEM PARA O SERVIDOR

    #------------------------------------------------------------------------
    #    REMENTENTE QUER ENVIAR MENSAGEM PARA DESTINATÁRIO - PASSO A PASSO
    #------------------------------------------------------------------------

    # Remetente carrega chave pública do destinatário e gera chave compartilhada
    public_key_receiver_loaded = serialization.load_pem_public_key(public_key_receiver_bytes, default_backend())
    shared_key_sender = derive_shared_key(private_key_sender, public_key_receiver_loaded)

    # Deriva chave simétrica usando HKDF no remetente
    salt = os.urandom(16)
    derived_key_sender = derive_symmetric_key(shared_key_sender, salt)

    # Cifra a mensagem no remetente
    message = b"Hello, ECC!, MOTO"
    iv = os.urandom(16)
    ciphertext = encrypt_message(derived_key_sender, iv, message)
    #----------------------------------------------------------------------------------------
    # ENVIA PARA O SERVIDOR A MENSAGEM CRIPTOGRAFADA es os vetores de inicialização salt e iv
    #----------------------------------------------------------------------------------------

    # Exibe os resultados do remetente
    print("Remetente:")
    print("Mensagem Original:", message.decode())
    print("Chave Compartilhada Remetente:", shared_key_sender.hex())
    print("IV (Vetor de Inicialização):", iv.hex())
    print("Mensagem Cifrada:", ciphertext.hex())

    #--------------------------------------------------------------------------------------
    # RECEBE DO SERVIDOR A MENSAGEM CRIPTOGRAFADA es os vetores de inicialização salt e iv
    #--------------------------------------------------------------------------------------

    #--------------------------------------------------------------------------
    #     DESTINATÁRIO RECEBE MENSAGEM DO REMETENDE - PASSO A PASSO
    #--------------------------------------------------------------------------

    # Destinatário carrega chave pública do remetente e gera chave compartilhada
    public_key_sender_loaded = serialization.load_pem_public_key(public_key_sender_bytes, default_backend())
    shared_key_receiver = derive_shared_key(private_key_receiver, public_key_sender_loaded)

    # Deriva chave simétrica usando HKDF no destinatário
    derived_key_receiver = derive_symmetric_key(shared_key_receiver, salt)

    # Destinatário decifra a mensagem
    decrypted_message = decrypt_message(derived_key_receiver, iv, ciphertext)

    # Exibe os resultados do destinatário
    print("\nDestinatário:")
    print("Chave Compartilhada Destinatário:", shared_key_receiver.hex())
    print("Mensagem Decifrada:", decrypted_message.decode())


if __name__ == "__main__":
    main()

