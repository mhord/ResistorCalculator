import argparse
import os.path

## This array is a list of E96 values; this is commonly the list that 1%
##  tolerance resistors are drawn from. It includes all the values in E24.
E96 = [10.0,	10.2,	10.5,	10.7,	11.0,	11.3,	11.5,	11.8,	12.1,	12.4,	12.7,	13.0,
13.3,	13.7,	14.0,	14.3,	14.7,	15.0,	15.4,	15.8,	16.2,	16.5,	16.9,	17.4,
17.8,	18.2,	18.7,	19.1,	19.6,	20.0,	20.5,	21.0,	21.5,	22.1,	22.6,	23.2,
23.7,	24.3,	24.9,	25.5,	26.1,	26.7,	27.4,	28.0,	28.7,	29.4,	30.1,	30.9,
31.6,	32.4,	33.2,	34.0,	34.8,	35.7,	36.5,	37.4,	38.3,	39.2,	40.2,	41.2,
42.2,	43.2,	44.2,	45.3,	46.4,	47.5,	48.7,	49.9,	51.1,	52.3,	53.6,	54.9,
56.2,	57.6,	59.0,	60.4,	61.9,	63.4,	64.9,	66.5,	68.1,	69.8,	71.5,	73.2,
75.0,	76.8,	78.7,	80.6,	82.5,	84.5,	86.6,	88.7,	90.9,	93.1,	95.3,	97.6]

## These are the E24 values, which are commonly the value options for 5%
##  tolerance resistors.
E24 = [1.0,	1.1,	1.2,	1.3,	1.5,	1.6,	1.8,	2.0,	2.2,	2.4,	2.7,	3.0,
3.3,	3.6,	3.9,	4.3,	4.7,	5.1,	5.6,	6.2,	6.8,	7.5,	8.2,	9.1]

## An array for holding results.
Stack = []

## This is the magic function that iterates over whatever the list is that gets
##  passed to it, and calculates the result.
def r_calc(Vin, Vout, r_list = E96,  r1_mult = 1, r2_mult = 1, o_list = Stack):
    ## We're going to iterate over the list of values we passed in.
    for i in r_list:
        ## We can pass in multipliers; maybe we want r1 to be in the range of
        ##  1k-10k, but R2 to be in the range 10k-100k. The multipler allows
        ##  us to do that.
        R1 = i*r1_mult
        ## Now, iterate across the list. Of course, this means our search size
        ##  is O-squared, but since the math is so easy, even large searches
        ##  go really quickly.
        for j in r_list:
            R2 = j*r2_mult
            ## Calculate the output voltage of this pair of resistors.
            Vtry = (Vin*R2)/(R1 + R2)
            ## Calculate the error of this pair of resistors.
            Tryerror = abs((Vtry-Vout)/Vout)
            ## Append the result matrix for this pair of resistors to the total
            ##  list. We're not going to attempt to sort it at this time.
            Try = [R1, R2, Vtry, Tryerror]
            Stack.append(Try)
    return o_list  ## return the resulting list

## We may want to know what the *real* error range is going to be; for example,
##  maybe we can tolerate a slight undervoltage, but a slight overvoltage is
##  catastrophic. This function calculates the tolerance range of the output
##  based on the resistor tolerances (assuming both resistors are of tolerance
##  tol). It does *not* account for the tolerance of Vin, of course.
def vout_err(Vin, Vout, R1Val, R2Val, tol):
    Tryerror = [0,0]
    Vtry = (Vin*(1-tol)*R2Val)/((1+tol)*R1Val + (1-tol)*R2Val)
    Tryerror[0] = (Vtry-Vout)/Vout
    Vtry = (Vin*(1+tol)*R2Val)/((1-tol)*R1Val + (1+tol)*R2Val)
    Tryerror[1] = (Vtry-Vout)/Vout
    return Tryerror

## This is our argument parser setup section. I'm not going to get into it; if you
##  really want to understand what's going on here, see the docs for argparse. Since
##  these all include a help string, they should be pretty obvious.
parser = argparse.ArgumentParser(description='Calculate real resistor values to form \
                                  a resistor divider.')
parser.add_argument('Vin', default = 5, type = float, help = "Input voltage.")
parser.add_argument('Vout', default = 3.3, type = float, help = "Desired output voltage.")
parser.add_argument('-f', action = 'store_true', help = "Use input file.") 
parser.add_argument('infile', nargs='?', type = argparse.FileType('r'))
parser.add_argument('-b', action = 'store_true', default = False, help = "Broaden search to 10x normal range.") 
parser.add_argument('-c', action = 'store_true', default = False, help = "Use coarse (E24) values.")
parser.add_argument('-n', default = 5, type = int, help = "Number of results to return.")
args = parser.parse_args()

## This will become the list that we pass to our r_calc function.
r_vals = []

## Based on our arguments, we should pick our list of resistor values.
if args.f == True:  ## Use an input file; our tolerance here is unknown, so leave it zero.
    for line in args.infile:
        r_vals.append(float(line))
    args.infile.close()
    tol = 0
elif args.c == True: ## The -c switch indicates that we want "coarse" (E24) values.
    r_vals = E24
    tol = .05  ## Pretty safe to assume that E24 resistors are 5% tolerance.
else:    ## Otherwise, we'll use E96.
    r_vals = E96
    tol = .01 ## E96 are *usually* 1% tolerance.

## Normally, we'll just do this and call it good...
results = r_calc(args.Vin, args.Vout, r_list = r_vals)
## HOWEVER, if the -b switch was invoked...
if args.b == True:
    ## ...and the -f switch was NOT invoked...
    if args.f == False:
        ## ..we're going to go back over the list of values again, this time broadening the search
        ##  out across three full orders of magnitude. For example, for E24 resistors...
        ## ...the first one searches with R1 10:91 and R2 1:9.1,
        r_calc(args.Vin, args.Vout, r_list = r_vals, r1_mult = 10, o_list = results)
        ## ...the second one is R1 1:9.1 and R2 10:91,
        r_calc(args.Vin, args.Vout, r_list = r_vals, r2_mult = 10, o_list = results)
        ## ...and this one is R1 .1:.91 and R2 10:91,
        r_calc(args.Vin, args.Vout, r_list = r_vals, r1_mult = .1, r2_mult = 10, o_list = results)
        ## ...and finally, R1 10:91 and R2 .1:.91.
        r_calc(args.Vin, args.Vout, r_list = r_vals, r1_mult = 10, r2_mult = .1, o_list = results)
        ## We just keep passing the same list back to each subsequent call, and adding the results
        ##  to the end of that list.

## Now that we've worked out the tolerance of all of our possible permutations, we want to sort the
##  list by the size of the nominal error.
sorted_results = sorted(results, key=lambda error: error[3])

## Finally, we want to report it to the user. The -n switch tells the program how many solutions
##  to report; by default, we report 5.
for m in range(args.n):
    tolerance = vout_err(args.Vin, args.Vout, sorted_results[m][0], sorted_results[m][1], tol)
    print 'R1: {:>5} R2: {:>5} Err (nom): {:.2%} Err (act): {:.2%} -> {:.2%} R1||R2= {:.1f}'.format( \
        sorted_results[m][0], \
        sorted_results[m][1], \
        sorted_results[m][3], \
        tolerance[0], \
        tolerance[1], \
        sorted_results[m][0]*sorted_results[m][1]/(sorted_results[m][0]+sorted_results[m][1]))
    
