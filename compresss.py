#!/usr/bin/env python3

import os
import sys
import heapq
import math

import numpy as np
import tkinter as tk

from subprocess import call
from PIL import Image
from tkinter import filedialog
from tkinter import messagebox

cmndlin = True

class HeapNode:
	def __init__(self, char, freq):
		self.char = char
		self.freq = freq
		self.left = None
		self.right = None

	def __lt__(self, other):
		return self.freq < other.freq

	def __eq__(self, other):
		if(other == None):
			return False
		if(not isinstance(other, HeapNode)):
			return False
		return self.freq == other.freq


class HuffmanCoding:
	def __init__(self, path):
		self.path = path
		self.heap = []
		self.codes = {}
		self.reverse_mapping = {}

	def make_frequency_dict(self, text):
		frequency = {}
		for character in text:
			if not character in frequency:
				frequency[character] = 0
			frequency[character] += 1
		return frequency

	def make_heap(self, frequency):
		for key in frequency:
			node = HeapNode(key, frequency[key])
			heapq.heappush(self.heap, node)

	def merge_nodes(self):
		while(len(self.heap)>1):
			node1 = heapq.heappop(self.heap)
			node2 = heapq.heappop(self.heap)

			merged = HeapNode(None, node1.freq + node2.freq)
			merged.left = node1
			merged.right = node2

			heapq.heappush(self.heap, merged)


	def make_codes_helper(self, root, current_code):
		if(root == None):
			return

		if(root.char != None):
			self.codes[root.char] = current_code
			self.reverse_mapping[current_code] = root.char
			return

		self.make_codes_helper(root.left, current_code + "0")
		self.make_codes_helper(root.right, current_code + "1")


	def make_codes(self):
		root = heapq.heappop(self.heap)
		current_code = ""
		self.make_codes_helper(root, current_code)


	def get_encoded_text(self, text):
		encoded_text = ""
		for character in text:
			encoded_text += self.codes[character]
		return encoded_text


	def pad_encoded_text(self, encoded_text):
		extra_padding = 8 - len(encoded_text) % 8
		for i in range(extra_padding):
			encoded_text += "0"

		padded_info = "{0:08b}".format(extra_padding)
		encoded_text = padded_info + encoded_text
		return encoded_text


	def get_byte_array(self, padded_encoded_text):
		if(len(padded_encoded_text) % 8 != 0):
			print("Encoded text not padded properly")
			exit(0)

		b = bytearray()
		no_of_bytes = len(padded_encoded_text) // 8
		
		str_dict = str(self.reverse_mapping)
		lis_bin = []
		lis_map = []
		
		
		l = 0
		while(l < len(padded_encoded_text)):
			byte = padded_encoded_text[l:l+8]
			lis_bin.append(int(byte, 2))
			l += 8
		
		for char in str_dict:
			lis_map.append(ord(char))

		no_of_bytes += len(lis_map)
		
		siz = math.ceil(no_of_bytes / 9)
		
		siz += 1 # for lengths
		
		rgba = np.zeros((siz, 3, 3), 'uint8')
		
		len1 = len(lis_bin)
		len2 = len(lis_map)
		
		
		m1 = len1 // 255
		a1 = len1 - m1 * 255
		m2 = m1 // 255
		a2 = m1 - m2 * 255
		m3 = m2 // 255
		a3 = m2 - m3 * 255
		
		
		rgba[0, 0, 0] , rgba[0, 0, 1], rgba[0, 0, 2], rgba[0, 1, 0] = m3, a3, a2, a1
		
		m1 = len2 // 255
		a1 = len2 - m1 * 255
		m2 = m1 // 255
		a2 = m1 - m2 * 255
		m3 = m2 // 255
		a3 = m2 - m3 * 255
		
		
		rgba[0, 1, 2] , rgba[0, 2, 0], rgba[0, 2, 1], rgba[0, 2, 2] = m3, a3, a2, a1
		
		mx = max(len1, len2)
		mn = min(len1, len2)
		
		if(mx == len1):
			lis_top = lis_bin
			lis_bot = lis_map
		else:
			lis_top = lis_map
			lis_bot = lis_bin
		
		l = 0
		m = 0
		
		flag = 0
		
		for i in range(1, siz):
			for j in range(3):
				for k in range(3):
					if(l < mx and m < mn):
						if(k!=2):
							rgba[i, j, k] = lis_top[l]
							l += 1
						else:
							rgba[i, j, k] = lis_bot[m]
							m += 1
					elif(l < mx):
						rgba[i, j, k] = lis_top[l]
						l += 1
					elif(m < mn):
						rgba[i, j, k] = lis_bot[m]
						m += 1
					else:
						flag = 1
						break
				if(flag):
					break
			if(flag):
				break
		
		
		img = Image.fromarray(np.uint8(rgba))
		output_path = os.path.splitext(self.path)[0] + ".png"
		img.save(output_path)

	def compress(self): 
		output_path = os.path.splitext(self.path)[0] + ".png"

		with open(self.path, 'r+') as file:
			text = file.read()
			text = text.rstrip()

			frequency = self.make_frequency_dict(text)
			self.make_heap(frequency)
			self.merge_nodes()
			self.make_codes()

			encoded_text = self.get_encoded_text(text)
			padded_encoded_text = self.pad_encoded_text(encoded_text)

			self.get_byte_array(padded_encoded_text)

		print("Compressed")
		return output_path


	""" functions for decompression: """

	def remove_padding(self, padded_encoded_text):
		padded_info = padded_encoded_text[:8]
		extra_padding = int(padded_info, 2)

		padded_encoded_text = padded_encoded_text[8:]
		encoded_text = padded_encoded_text[:-1*extra_padding]

		return encoded_text

	def decode_text(self, encoded_text):
		current_code = ""
		decoded_text = ""	
		
		for bit in encoded_text:
			current_code += bit
			if(current_code in self.reverse_mapping):
				character = self.reverse_mapping[current_code]
				decoded_text += character
				current_code = ""

		return decoded_text


	def decompress(self):
		filename, file_extension = os.path.splitext(self.path)
		output_path = filename + "_decompressed" + ".txt"
		
		arr2 = np.array(Image.open(self.path))
		
		if(arr2[0, 1, 1] != 0):
			if cmndlin: # commandliner
				print("Invalid signature in supplied file")
			else: # GUIer
				messagebox.showerror("Error", "Invalid signature in supplied file")
			exit()
		
		
		m3, a3, a2, a1 = arr2[0, 0, 0] , arr2[0, 0, 1], arr2[0, 0, 2], arr2[0, 1, 0]
		len1 = ((m3 * 255 + a3) * 255 + a2) * 255 + a1
		
		m3, a3, a2, a1 = arr2[0, 1, 2] , arr2[0, 2, 0], arr2[0, 2, 1], arr2[0, 2, 2]
		len2 = ((m3 * 255 + a3) * 255 + a2) * 255 + a1
		
		
		siz = math.ceil((len1 + len2) / 9)
		
		siz += 1 # for lengths
		
		lis_top = []
		lis_bot = []
		
		l = 0
		m = 0
		
		mx = max(len1, len2)
		mn = min(len1, len2)
		
		
		flag = 0
		
		for i in range(1, siz):
			for j in range(3):
				for k in range(3):
					if(l < mx and m < mn):
						if(k!=2):
							lis_top.append(arr2[i, j, k])
							l += 1
						else:
							lis_bot.append(arr2[i, j, k])
							m += 1
					elif(l < mx):
						lis_top.append(arr2[i, j, k])
						l += 1
					elif(m < mn):
						lis_bot.append(arr2[i, j, k])
						m += 1
					else:
						flag = 1
						break
				if(flag):
					break
			if(flag):
				break
		
		if(mx == len1):
			lis_bin = lis_top
			lis_map = lis_bot
		else:
			lis_map = lis_top
			lis_bin = lis_bot
		
		
		str_dict = ""
		
		for n in lis_map:
			str_dict += chr(n)
		
		
		self.reverse_mapping = eval(str_dict)
		
		temp = bytearray(lis_bin)
		
		with open(output_path, 'w') as output:
			bit_string = ""

			i = 0
			while(i < len1):
				byte = bytes(temp[i:i+1])
				byte = ord(byte)
				bits = bin(byte)[2:].rjust(8, '0')
				bit_string += bits
				i += 1

			encoded_text = self.remove_padding(bit_string)
			
			decompressed_text = self.decode_text(encoded_text)

			output.write(decompressed_text)

		print("Decompressed")
		return output_path

if __name__ == "__main__":
	
	if len(sys.argv) == 1:
		cmndlin = False
		root = tk.Tk()
		root.withdraw()
		fname = filedialog.askopenfilename(title = "Select file to compress/decompress",
										   filetypes = [("Text Files", ".txt"), ("PNG Images", ".png")])
									   
	elif len(sys.argv) > 1 and len(sys.argv) < 3:
		fname = sys.argv[1]
		if(not os.path.isfile(fname)):
			print('File '+fname+' does not exist\n')
			exit()
	
	else:
		print("Incorrect number of arguments supplied\n")
		exit()
	
	if(fname):
		exten = fname.split('.')
	
		if(exten[-1] not in ['txt', 'png']):
			print('Incorrect file format\n[Supported extensions: .txt & .png]\n')
			exit()
	
		h = HuffmanCoding(fname)
		
		if exten[-1] == 'txt':
			print(h.compress())
		elif exten[-1] == 'png':
			print(h.decompress())
	else:
		print("File was not chosen")
