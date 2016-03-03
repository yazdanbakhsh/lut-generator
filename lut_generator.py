#!/usr/bin/python

# Amir Yazdanbakhsh
# May 25 - 2014 - version 2.0

import sys
import math
from decimal import *


# returns an string of the converter module
def converter_module(input_size, fraction, lut_size, rangesize):

  input_max   = int(input_size)-1
  lut_max     = int(int.bit_length(int(lut_size)-1)) - 1
  integer_part = int(int.bit_length(int(rangesize)-1)) - 1

  converter_module = ""
  converter_module += "module converter(a, index);\n"
  converter_module += "\tinput  [%s:0] a;\n" % (str(input_max))
  converter_module += "\toutput [%s:0] index;\n\n" % (str(lut_max))

  converter_module += "\tassign index[%s]\t= a[%s];\n" % (str(lut_max), str(input_max))
  converter_module += "\tassign index[%s:%s]\t= a[%s:%s];\n" % (str(lut_max-1), str(lut_max-integer_part), str(int(fraction+integer_part-1)), str(int(fraction)))
  fraction_size = lut_max-integer_part
  converter_module += "\tassign index[%s:0]\t= a[%s:%s];\n" % (str(fraction_size-1), str(int(fraction)-1), str(int(fraction)-fraction_size))
  converter_module += "endmodule"

  return converter_module

pass;

def header_fun(input_size, lut_size, function):

  header  = ""
  header += "module %s_lut(a, out);\n" % (function)
  header += "\tinput  [%s:0] a;\n" % (input_size-1)
  header += "\toutput reg [%s:0] out;\n" % (input_size-1)
  header += "\twire   [%s:0] index;\n\n" % (int.bit_length(int(lut_size)-1) - 1)
  #header += "\treg    [%s:0] mem [0:%s]" % (input_size-1, int(lut_size))

  header += "\talways @(index)\n"
  header += "\tbegin\n"
  header += "\t\tcase(index)\n"
  return header
pass;


def footer_fun():

  footer = ""
  footer += "\t\tendcase\n"
  footer += "\tend\n"
  footer += "\tconverter U0 (a, index);\n\n"
  footer += "endmodule\n\n"
  return footer
pass;

def convert2dec(value_str, tot_bits, frac_bits):
  sign_str=value_str[:1]
  int_str=value_str[1:tot_bits-frac_bits]
  flt_str=value_str[tot_bits-frac_bits:]

  if(sign_str=='1'):
    return -1.0 * float(int(int_str,2) + int(flt_str,2)/float(math.pow(2.0,frac_bits)))
  else:
    return 1.0 * float(int(int_str,2) + int(flt_str,2)/float(math.pow(2.0,frac_bits)))
pass;

def sigmoid(value,steepness):
    return (1.0/float(1.0+math.exp(-2.0*steepness*value)))
pass;


def calculate_function(func, value):
  if(func == "sin"):
    return math.sin(value)
  elif (func == "cos"):
    return math.cos(value)
  elif (func == "sigmoid"):
    return sigmoid(value, 0.5)
  elif (func == "acos"):
    return math.acos(value)
  elif (func == "asin"):
    return math.asin(value)
pass;

def convert2fixed(value, tot_bits, frac_bits):

  (frac_value, int_value)  = math.modf(value)
  flag = 0
  if(abs(int_value) >= pow(2.0, tot_bits-frac_bits-1)):
    int_value = pow(2.0, tot_bits-frac_bits-1)-1

  if(abs(frac_value) > ((math.pow(2.0,frac_bits)-1) / math.pow(2.0,frac_bits))):
    frac_value = (math.pow(2.0,frac_bits)-1) / math.pow(2.0,frac_bits)
    flag = 1;
  else:
    frac_value = (frac_value * math.pow(2.0,frac_bits))

  int_value  = int(int_value)
  if (flag==0):
    frac_value = round(frac_value)
  else:
    #print 'read'
    frac_value = (math.pow(2.0,frac_bits)-1)
  flag = 0

  int_str   = '{0:032b}'.format(int(int_value)) # one bit for sign bit
  frac_str  = '{0:032b}'.format(int(frac_value))

  int_str  = int_str[32-(tot_bits-frac_bits)+1:32]
  frac_str = frac_str[32-(frac_bits):32]

  #print "Integer:            " + int_str
  #print "Fraction:           " + frac_str 

  if(value >=0):
    return "0" + int_str + frac_str
  else:
    return "1" + int_str + frac_str
pass;

def main():

  if(len(sys.argv) != 6):
    print "Usage: lut_generate <# bits> <# fractions> <# lut entries> <range> <sin|cos|asin|acos|sigmoid>"
    exit(1)

  print "Generating LUT table for %s function...\n" %(sys.argv[5])
  out_fn = open(sys.argv[5] + "_lut.v", "w")

  data_out = open(sys.argv[5] + ".list", "w")

  # Positive part
  init = 0
  input_range = int(sys.argv[4])
  lut_entries = float(sys.argv[3])
  bits = int(sys.argv[1])
  frac = int(sys.argv[2])
  inc  = input_range / lut_entries
  func = sys.argv[5]



  out_fn.write(header_fun(bits, lut_entries, func))


  index = 0
  start = init + (inc / 2.0)
  for i in range(int(lut_entries/2.0)):
    curr_val  = calculate_function(func, start)
    fixed_val = convert2fixed(curr_val, bits, frac)

    out_fn.write("\t\t\t%s'd%s: out = %s'b%s; // input=%s, output=%s\n" % (str(int.bit_length(int(lut_entries)-1)), str(index), str(bits), fixed_val, str(start), str(curr_val))) 
    data_out.write(fixed_val)
    data_out.write("\n") 
    index += 1
    start += inc
  pass;

  start = init - (inc / 2.0)
  for i in range(int(lut_entries/2.0)):
    curr_val  = calculate_function(func, start)
    fixed_val = convert2fixed(curr_val, bits, frac)

    out_fn.write("\t\t\t%s'd%s: out = %s'b%s; // input=%s, output=%s\n" % (str(int.bit_length(int(lut_entries)-1)), str(index), str(bits), fixed_val, str(start), str(curr_val))) 
    data_out.write(fixed_val)
    data_out.write("\n") 
    index += 1
    start -= inc
  pass;

  out_fn.write(footer_fun())
  out_fn.write(converter_module(bits, frac, lut_entries, input_range))
pass;



if __name__ == "__main__":
  main()