
import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.security.Key;

import javax.crypto.Cipher;
import javax.crypto.spec.SecretKeySpec;

public class BlowEncDec {
	
	private static final String ALGORITHM = "Blowfish";
	private static String keyString = "DesireSecretKey";

	public static void encrypt(File inputFile, File outputFile)
			throws Exception {
		doCrypto(Cipher.ENCRYPT_MODE, inputFile, outputFile);
		System.out.println("File encrypted successfully!");
	}

	public static void decrypt(File inputFile, File outputFile)
			throws Exception {
		doCrypto(Cipher.DECRYPT_MODE, inputFile, outputFile);
		System.out.println("File decrypted successfully!");
	}

	private static void doCrypto(int cipherMode, File inputFile,
			File outputFile) throws Exception {

		Key secretKey = new SecretKeySpec(keyString.getBytes(), ALGORITHM);
		Cipher cipher = Cipher.getInstance(ALGORITHM);
		cipher.init(cipherMode, secretKey);

		FileInputStream inputStream = new FileInputStream(inputFile);
		byte[] inputBytes = new byte[(int) inputFile.length()];
		inputStream.read(inputBytes);

		byte[] outputBytes = cipher.doFinal(inputBytes);

		FileOutputStream outputStream = new FileOutputStream(outputFile);
		outputStream.write(outputBytes);

		inputStream.close();
		outputStream.close();

	}

	public static void main(String[] args) {
		

		String file_name = args[2];
		keyString = args[1] ;
		char choice = args[0].charAt(0);
		File inputFile = new File(file_name);
		String enc_file = file_name + ".bloen";
		File encryptedFile = new File(enc_file);
		String dec_file = file_name.substring( 0 , file_name.length() -6);
		File decryptedFile = new File(dec_file);

		try {
			if(choice == 'e')
			{
			BlowEncDec.encrypt(inputFile, encryptedFile);
		}else if (choice == 'd')
		{
			BlowEncDec.decrypt(inputFile, decryptedFile);
		}else 
		{
			System.out.println("Invalid choice ");
		}
		} catch (Exception e) {
			e.printStackTrace();
		}
		
		
	}
}