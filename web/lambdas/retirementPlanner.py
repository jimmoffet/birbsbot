import json
import logging
import calendar
import math
import traceback

log = logging.getLogger()

### Global Variables ###

# savings
foreverHomePurchaseMinReserve = 25000
rentalHomePurchaseMinReserve = 50000
startingSavings = 60000
# real estate
hollandMortgage = 2400
hollandUtilites = 400
# foreverHomeMortgage = 4200
foreverHomeUtilities = 500
vacancyRate = 0.04
propManRate = 0.09  # includes half month for new tenants
# lombardHollandNetIncome = 2000  # top-line ~2700, ~2000 after vacancy and maintenance
# lombardHollandEquity = 250000
rentalIncomeNominal = 120000  # let's take 10% of the top as a cushion
# income
grossMonthly = 14378
healthDeduction = 460
monthlyPensionNet = 2750
monthlyPensionDict = {
    50: [2420, 12.91],
    51: [2575, 12.91],
    52: [2730, 12.83],
    53: [2884, 12.91],
    54: [3039, 12.83],
    55: [3193, 12.91],
    56: [3348, 12.83],
    57: [3502, 12.83],
    58: [3656, 12.83],
    59: [3810, 12.83],
    60: [3964, 12.83],
    61: [4118, 12.75],
    62: [4271, 28.75],
    63: [4616, 29.25],
    64: [4967, 35.33],
    65: [5391, 35.33],
    66: [5815, 36],
    67: [6247, 36],
}
pensionStartAge = 55
lifeDeduction = grossMonthly * 0.0042
fersDeduction = grossMonthly * 0.044
employerContributionRate = 0.05
jimContributionRate = 0.05
employer401kcontribution = grossMonthly * employerContributionRate
jim401kContribution = grossMonthly * employerContributionRate
total401kContribution = jim401kContribution + employer401kcontribution
carleyPrePPSsavings = 850
carleyPPSsavings = 2800
# taxes
fed = 0.1395
med = 0.0153
oasd = 0.0653
state = 0.0872
orTransit = 0.0010
orWorkerComp = 0.0002
taxes = [fed, med, oasd, state, orTransit, orWorkerComp]
# explicit safety margins
rentalIncomeSafetyMargin = 0.1


def getSS(startAge, retireAge, currentAge):
    fullBenefitsAge = 67
    if currentAge < retireAge and currentAge < fullBenefitsAge:
        return 0
    ssDict = {
        55: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        56: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        57: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        58: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        59: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        60: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        61: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        62: [2340, 2393, 2447, 2500, 2553, 2606, 2658, 2711, 0, 0, 0],
        63: [2507, 2563.78, 2621.63, 2678.41, 2735.2, 2791.98, 2847.69, 2904.47, 2955, 0, 0],
        64: [2674, 2734.56, 2796.27, 2856.83, 2917.4, 2977.96, 3037.38, 3097.95, 3151.84, 3205, 0],
        65: [2897, 2963, 3029, 3095, 3161, 3226, 3291, 3356, 3414, 3472, 3528],
    }

    if startAge < retireAge:
        startAge = retireAge
    start = max(62, min(65, startAge))
    retire = max(55, min(65, retireAge))
    # print("start now: ", start)
    # print("retire now: ", retire)
    pension = 0 if currentAge < 62 else ssDict[start][retire - 55]
    return pension


def getERS(startAge, retireAge, currentAge):
    fullBenefitsAge = 62
    if currentAge < retireAge:
        return 0
    ersDict = {
        55: [834, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        56: [932, 1049, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        57: [1031, 1155, 1279, 0, 0, 0, 0, 0, 0, 0, 0],
        58: [1133, 1264, 1396.5, 1531, 0, 0, 0, 0, 0, 0, 0],
        59: [1237, 1377.5, 1514, 1659.5, 1801, 0, 0, 0, 0, 0, 0],
        60: [1345, 1491, 1638, 1788, 1940.5, 2297, 0, 0, 0, 0, 0],
        61: [1455, 1610.5, 1762, 1923.5, 2080, 2347, 2513, 0, 0, 0, 0],
        62: [1569, 1730, 1851, 2059, 2180, 2397, 2571, 2744, 0, 0, 0],
        63: [1610, 1777, 1940, 2112.5, 2280, 2457.5, 2629, 2811, 2990, 0, 0],
        64: [1656, 1824, 1995.5, 2166, 2343, 2518, 2699.5, 2878, 3068, 3253, 0],
        65: [1707, 1879, 2051, 2229, 2406, 2588, 2770, 2956, 3146, 3339, 3537],
    }
    startAge = 62 if retireAge < 60 else 60
    if startAge < retireAge:
        startAge = retireAge
    start = max(55, min(65, startAge))
    retire = max(55, min(65, retireAge))
    # print("start now: ", start)
    # print("retire now: ", retire)
    pension = 0 if currentAge < 55 else ersDict[start][retire - 55]
    return pension


def getPension(startAge, retireAge, currentAge):
    if currentAge < retireAge:
        return 0
    ss = getSS(startAge, retireAge, currentAge)
    ers = getERS(startAge, retireAge, currentAge)
    return ss + ers


# import sys
# retireAge = 55
# currentAge = 62
# ss = getSS(62, retireAge, currentAge)
# ers = getERS(62, retireAge, currentAge)
# print("ss: ", ss)
# print("ers: ", ers)
# print("totalPension: ", ss + ers)
# sys.exit()


def calculateNetWages(grossMonthly, healthDeduction, monthly401k, taxes, lifeDeduction, fersDeduction):
    fed = taxes[0]
    med = taxes[1]
    oasd = taxes[2]
    state = taxes[3]
    orTransit = taxes[4]
    orWorkerComp = taxes[5]
    preTaxWages = grossMonthly - monthly401k
    totalTaxRate = fed + med + oasd + state + orTransit + orWorkerComp
    tax = preTaxWages * totalTaxRate
    postTaxWages = preTaxWages - tax
    postTaxDeductions = healthDeduction + lifeDeduction + fersDeduction
    netWages = postTaxWages - postTaxDeductions
    return netWages


# import sys
# net = calculateNetWages(grossMonthly, healthDeduction, 718, taxes, lifeDeduction, fersDeduction)
# print(net)
# sys.exit()


def getMonthlyRentalIncome(
    rentalHomes, monthNumber, year, rentalIncomeSafetyMargin, inflation, vacancyRate, propManRate, realMortgage=True
):
    """
    120000 - 4800 - 66000 - 9000 - 8400 = 36600 - ((36600 - 32727) * 0.25)
    rent - 4% vacancy - mortgage - maint - propman = 36600 - ( (36600 - 32727 depreciation) * 0.25 tax rate = 968.25 tax) = 35632 net income
    """

    totalMonthlyIncome = 0

    # 900k rental # 4900 = (784 + 2913) + 1200
    # 1.25M Rummer house # 7146 = (1162 + 4316) + 1667

    # 900k rental
    # mortgagePmt = 4900
    # 1.25M Rummer house # 7146 = (1162 + 4316) + 1667

    for id, rentalHome in rentalHomes.items():
        mortgagePmt = rentalHome["monthlyPayment"] * 12  # 5k per month including taxes and fees

        if realMortgage:
            yearsInFuture = year - rentalHome["purchaseYear"]
            futureDollar = math.pow((1 + inflation), yearsInFuture) if yearsInFuture > 0 else 1
            mortgagePMTfutureValue = mortgagePmt / futureDollar
            mortgagePmt = mortgagePMTfutureValue

        taxAndInsurance = mortgagePmt * 0.32
        principleAndInterest = mortgagePmt * 0.68
        monthsSincePurchase = monthNumber - rentalHome["purchaseMonth"]
        rentalAge = monthsSincePurchase / 360
        interestOnly = principleAndInterest * (0.73 * (1 - rentalAge))  # 1-(350/360) = 2.7%
        principleOnly = principleAndInterest - interestOnly
        mortgageDeduction = interestOnly + taxAndInsurance

        rentalIncomeNominal = rentalHome["grossMonthlyIncome"] * 12
        rentalIncomeNominal = rentalIncomeNominal * (1 - rentalIncomeSafetyMargin)

        if rentalHome["isPaidOff"]:
            mortgagePmt = mortgagePmt * 0.32  # prop taxes and insurance
            mortgageDeduction = taxAndInsurance

        # mortgageDeduction = mortgagePmt # debug
        vacancyCost = rentalIncomeNominal * vacancyRate
        maintenanceCost = rentalHome["purchasePrice"] * 0.01  # 1% of total property value
        propManCost = rentalIncomeNominal * propManRate
        grossAnnualIncome = rentalIncomeNominal - vacancyCost - mortgagePmt - maintenanceCost - propManCost
        depreciation = rentalHome["purchasePrice"] / 27.5
        taxableIncome = (
            rentalIncomeNominal - vacancyCost - mortgageDeduction - maintenanceCost - propManCost - depreciation
        )
        taxes = taxableIncome * 0.25
        netAnnualIncome = grossAnnualIncome - taxes
        monthlyIncome = netAnnualIncome / 12
        # if monthsSincePurchase == 1:
        #     print("In month 1, annual mortgageDeduction is: ", mortgageDeduction)
        #     print("In month 1, monthly net rental profit is: ", monthlyIncome)
        # if monthsSincePurchase == 359:
        #     print("In month 359, annual mortgageDeduction is: ", mortgageDeduction)
        #     print("In month 359, monthly net rental profit is: ", monthlyIncome)
        totalMonthlyIncome += monthlyIncome
    return totalMonthlyIncome


def iterateMonthlyForecast(
    months,
    retireAge,
    retireMonth,
    startingSavings,
    monthlyBudget,
    hollandSavingsPrePPS,
    hollandSavingsPPS,
    foreverHomeSavings,
    maxRentals,
    travelBudget,
    oopsBudget,
    inflation,
    early40sReduction,
    retirementReduction,
    returnRate,
    postRetirementReturnRate,
    foreverHomeCost,
    extraHollandMonths,
    sellRentals=False,
):
    lombardHollandNetIncome = 2000  # 2700 before vacancy/maintenance
    lombardHollandEquity = 250000

    # extraHollandMonths = 3
    foreverHomeDelayedMonth = -1

    foreverHomeRenovationCost = 35000
    completedForeverHomeRenovations = 0
    maxForeverHomeRenovations = 2

    age = 39
    pensionStartAge = 55
    ssStartAge = 62

    # retireAge = age + (retireMonth / 12)
    # retireAge = 0

    retired = False
    savings = startingSavings
    lowSavings = startingSavings
    numRentals = 0
    savingsAt75 = 0
    savingsAt85 = 0
    budgetAt85 = 999999999
    equityAt75 = 0
    equityAt85 = 0
    equity = lombardHollandEquity
    rentalEquity = 0

    retirementDate = ""

    rentalHomePurchaseMonths = []
    incomeAt75 = 0
    incomeAt85 = 0
    rentalHomes = {}
    numRentalsPaidOff = 0
    otherIncome = 0
    equity = 0
    pensionIncome = 0
    startYear = 2022
    year = 2022
    popRental = 0
    shouldPop = False
    # foreverHomeCost = 750000
    foreverHomeReno = 25000
    foreverHomeEquity = 0
    foreverHome = False
    foreverHomeDate = ""
    foreverHomeMortgage = foreverHomeCost * 0.0056
    foreverHomePurchaseMonth = 0
    foreverHomeUtilities = 500

    studentLoans = 450 + 525  # fedloan + firstmark + carley's loans = 1175
    carPayment = 0

    preHollandSavingsPrePPS = hollandSavingsPrePPS
    preHollandSavingsPPS = hollandSavingsPPS
    preForeverHomeSavings = foreverHomeSavings

    monthlySavings = hollandSavingsPrePPS
    currentMonthlyBudget = monthlyBudget
    currentMonthlySavings = monthlySavings

    for i in range(1, months):
        if i % 12 == 7:
            year += 1
        monthName = calendar.month_name[((i + 5) % 12) + 1]

        if i == 96:
            studentLoans = 450  # fedloan + firstmark + carley's loans = 1175
        elif i == 360:
            studentLoans = 0

        if i == 24:
            carPayment = 600
            studentLoans = 525 + 450 + 200
        if i == 96:
            carPayment = 0

        hollandSavingsPrePPS = preHollandSavingsPrePPS - carPayment - studentLoans
        hollandSavingsPPS = preHollandSavingsPPS - carPayment - studentLoans
        foreverHomeSavings = preForeverHomeSavings - carPayment - studentLoans

        # monthlySavings = hollandSavingsPrePPS
        # currentMonthlySavings = monthlySavings

        # hollandSavingsPrePPS = hollandSavingsPrePPS - carPayment - studentLoans
        # hollandSavingsPPS = hollandSavingsPPS - carPayment - studentLoans
        # foreverHomeSavings = foreverHomeSavings - carPayment - studentLoans
        # if not foreverHome:
        #     print("hollandSavingsPrePPS final: ", hollandSavingsPrePPS)
        # # print("hollandSavingsPPS final: ", hollandSavingsPPS)
        # # print("foreverHomeSavings final: ", foreverHomeSavings)
        if i == 1:
            monthlySavings = hollandSavingsPrePPS
            currentMonthlySavings = monthlySavings
            # print("currentMonthlySavings is: ", currentMonthlySavings)

        if i == 24:
            monthlySavings = hollandSavingsPrePPS
            currentMonthlySavings = monthlySavings

        if 12 < i < 30:
            currentMonthlySavings = monthlySavings - carleyPrePPSsavings  # Carley not working during gtep
            # if not foreverHome:
            #     print("currentMonthlySavings without carleyPrePPSsavings: ", currentMonthlySavings)

        if i == 30:  # assume it takes C 6 months to start earning 53k
            monthlySavings = hollandSavingsPPS
            currentMonthlySavings = monthlySavings
            # if not foreverHome:
            #     print("currentMonthlySavings is now: ", currentMonthlySavings)

        if i == 96:  # assume it takes C 6 months to start earning 53k
            monthlySavings = hollandSavingsPPS
            currentMonthlySavings = monthlySavings
            if foreverHome:
                monthlySavings = foreverHomeSavings
                currentMonthlySavings = monthlySavings

        for id, rentalHome in rentalHomes.items():
            rentalHomePurchaseMonth = rentalHome["purchaseMonth"]
            if id == 2 and shouldPop:
                equityFirstTwo = rentalHomes[1]["equity"] + rentalHomes[2]["equity"]
                preSaleRepairs = 0  # assume repair costs are paid by home value increase over inflation (this is dicey)
                closingCosts = 90000
                if equityFirstTwo > (900000 + preSaleRepairs + closingCosts) and shouldPop:
                    # print("Date:", monthName, "", year)
                    # print("rentalHomes prior to sale of second rental:", rentalHomes)
                    saleValue = rentalHomes[2]["equity"] - 90000
                    popRental = 2
                    rentalHomes[1]["equity"] = 900000
                    rentalHomes[1]["isPaidOff"] = True
                    excessCash = equityFirstTwo - (900000 + preSaleRepairs + closingCosts)
                    savings += excessCash
                    maxRentals -= 1
            if (i - rentalHomePurchaseMonth) == 360:
                numRentalsPaidOff += 1
                rentalHomes[id]["isPaidOff"] = True
                rentalHome["equity"] = 900000

        if popRental and shouldPop:
            rentalHomes.pop(popRental)
            # print("rentalHomes after sale of second rental:", rentalHomes)
            popRental = 0
            shouldPop = False

        if len(rentalHomes.keys()) == 0:
            otherIncome = lombardHollandNetIncome
        else:
            otherIncome = getMonthlyRentalIncome(
                rentalHomes, i, year, rentalIncomeSafetyMargin, inflation, vacancyRate, propManRate, realMortgage=True
            )

        if not foreverHome:
            currentMonthlyBudget = monthlyBudget * (1 - early40sReduction)
            currentMonthlySavings = currentMonthlySavings + (monthlyBudget * early40sReduction)
            # if not foreverHome:
            #     print("currentMonthlySavings after early 40s reduction is: ", currentMonthlySavings)
        else:
            currentMonthlyBudget = monthlyBudget

        retireAge = 39 + (retireMonth / 12)
        currentAge = 39 + (i / 12)

        if retireAge > pensionStartAge:
            pensionStartAge = retireAge

        if retireAge > ssStartAge:
            ssStartAge = retireAge

        # if math.trunc(currentAge) < pensionStartAge:
        #     pensionIncome = 0
        # elif pensionIncome == 0:
        ssIncome = getSS(math.trunc(ssStartAge), math.trunc(retireAge), math.trunc(currentAge))
        ersIncome = getERS(math.trunc(pensionStartAge), math.trunc(retireAge), math.trunc(currentAge))
        pensionIncome = ssIncome + ersIncome
        # if i % 12 == 0:
        #     print(
        #         "ssStartAge: ",
        #         ssStartAge,
        #         "pensionStartAge: ",
        #         pensionStartAge,
        #         "retireAge: ",
        #         retireAge,
        #         "currentAge: ",
        #         currentAge,
        #         "ssIncome: ",
        #         ssIncome,
        #         "ersIncome: ",
        #         ersIncome,
        #     )
        # if i % 12 == 0:
        #     print("pensionStartAge: ", pensionStartAge)
        #     print("math.trunc(retireAge): ", math.trunc(retireAge))
        #     print("math.trunc(currentAge): ", math.trunc(currentAge))
        #     print("pensionIncome: ", pensionIncome)
        # if age >= pensionStartAge:
        #     minAge = math.trunc(age) if age <= 67 else 67
        #     pensionIncome = monthlyPensionDict[minAge][0]
        #     # pensionIncome = monthlyPensionNet
        # else:
        #     pensionIncome = 0

        if foreverHome and (i - foreverHomePurchaseMonth) == 360:
            foreverHomeMortgage = foreverHomeMortgage * 0.32

        if age == 70:
            travelBudget = 250

        postRetirementAnnualIncome = 0
        postRetirementMonthlyIncome = (postRetirementAnnualIncome / 12) * 0.75
        if i >= retireMonth:
            if age >= 67:
                postRetirementMonthlyIncome = 0
            retired = True
            retirementDate = monthName + " " + str(year)
            currentMonthlyBudget = monthlyBudget * (1 - retirementReduction)
            currentMonthlySavings = (
                pensionIncome
                + postRetirementMonthlyIncome
                - currentMonthlyBudget
                - travelBudget
                - oopsBudget
                - foreverHomeMortgage
                - foreverHomeUtilities
                - carPayment
                - studentLoans
            )

        savings = savings + currentMonthlySavings + otherIncome

        if (
            foreverHome
            and (len(rentalHomes.keys()) > 0 or maxRentals == 0)
            and savings > 100000
            and completedForeverHomeRenovations < maxForeverHomeRenovations
        ):
            # print("subtracting foreverhome renovation cost from savings")
            savings = savings - foreverHomeRenovationCost
            completedForeverHomeRenovations += 1

        if savings > ((foreverHomeCost * 0.2) + foreverHomeReno + foreverHomePurchaseMinReserve) and not foreverHome:
            if foreverHomeDelayedMonth == -1:
                foreverHomeDelayedMonth = i + extraHollandMonths
            if i == foreverHomeDelayedMonth:
                foreverHome = True
                # print("Savings at forever home purchase: ", savings)
                savings = savings - ((foreverHomeCost * 0.2) + foreverHomeReno)
                foreverHomeEquity = (foreverHomeCost * 0.2) + foreverHomeReno
                foreverHomePurchaseMonth = i
                monthlySavings = foreverHomeSavings
                currentMonthlySavings = monthlySavings
                # print("currentMonthlySavings after foreverhome is: ", currentMonthlySavings)
                # print("Bought forever home in ", monthName, "", year)
                foreverHomeDate = monthName + " " + str(year)

                # LOMBARD HOLLAND EQUITY ASSUMES CLOSING COSTS / REPAIRS HAVE BEEN PAID

                # print("Sold Lombard and Holland in ", monthName, "", year)
                capGainsTaxRate = 0.15
                savings = savings + (lombardHollandEquity * (1 - capGainsTaxRate))
                lombardHollandNetIncome = 0
                lombardHollandEquity = 0

        if savings > (225000 + rentalHomePurchaseMinReserve) and len(rentalHomes.keys()) < maxRentals:
            if foreverHomeDelayedMonth != -1 and i > (foreverHomeDelayedMonth + 12):
                savings = savings - 225000
                rentalEquity = rentalEquity + 225000
                # rentalHomePurchaseMonths.append(i)
                largestKey = max(rentalHomes.keys()) if len(rentalHomes.keys()) > 0 else 0
                rentalHomes[largestKey + 1] = {
                    "purchaseMonth": i,
                    "purchaseYear": year,
                    "equity": 225000,
                    "purchasePrice": 900000,
                    "monthlyPayment": 5000,
                    "grossMonthlyIncome": 10000,
                    "isPaidOff": False,
                }
                # print("Bought a 900k rental property in ", monthName, "", year)

        savingsReturnRate = returnRate - inflation
        if retired:
            savingsReturnRate = postRetirementReturnRate - inflation

        if foreverHome and (i - foreverHomePurchaseMonth) <= 360:
            foreverHomeEquity = foreverHomeEquity + ((foreverHomeCost - (foreverHomeCost * 0.2)) * (0.033 / 12))
        if foreverHome and (i - foreverHomePurchaseMonth) > 360:
            foreverHomeEquity = foreverHomeCost

        for id, rentalHome in rentalHomes.items():
            tempRentalEquity = 0
            loanAmount = 900000 - 225000
            if (i - rentalHome["purchaseMonth"]) <= 360:
                tempRentalEquity = rentalHome["equity"] + (loanAmount * (0.033 / 12))
                rentalHomes[id]["equity"] = tempRentalEquity
            if (i - rentalHome["purchaseMonth"]) > 360:
                rentalHomes[id]["equity"] = rentalHomes[id]["purchasePrice"]

        rentalEquity = 0
        for id, rentalHome in rentalHomes.items():
            rentalEquity += rentalHomes[id]["equity"]

        equity = foreverHomeEquity + lombardHollandEquity + rentalEquity

        if age == 75:
            savingsAt75 = savings
            equityAt75 = equity
            incomeAt75 = currentMonthlySavings + otherIncome
            # print("Age is 75: ")
            # print("retireAge: ", (39 + (retireMonth / 12)))
            # print("savingsAt75: ", savingsAt75)
            # print("pensionIncome: ", pensionIncome)
            # print("postRetirementMonthlyIncome: ", postRetirementMonthlyIncome)
            # print("currentMonthlyBudget: ", currentMonthlyBudget)
            # print("travelBudget: ", travelBudget)
            # print("oopsBudget: ", oopsBudget)
            # print("foreverHomeMortgage: ", foreverHomeMortgage)
            # print("foreverHomeUtilities: ", foreverHomeUtilities)
            # print("pensionIncome: ", pensionIncome)
            # print("carPayment: ", carPayment)
            # print("studentLoans: ", studentLoans)
            # print("currentMonthlySavings: ", incomeAt75)

            budgetAt75 = currentMonthlyBudget
        if age == 85:
            savingsAt85 = savings
            equityAt85 = equity
            incomeAt85 = currentMonthlySavings + otherIncome
            budgetAt85 = currentMonthlyBudget

        if savings < lowSavings:
            lowSavings = savings
            if lowSavings < 24999 and sellRentals:
                # print("Need to sell oldest rental in ", monthName, "", year) # only do this once and assume we take a haircut in addition to 10% sales cost
                if rentalHomes:
                    oldestRentalID = min(rentalHomes.keys())
                    oldestRental = rentalHomes[oldestRentalID]
                    # tempMonthName = calendar.month_name[((oldestRental["purchaseMonth"] + 5) % 12) + 1]
                    # tempYear = startYear + ((oldestRental["purchaseMonth"] + 5) // 12)
                    oldestRentalEquity = rentalHomes[oldestRentalID]["equity"]
                    # let's say we have 350k in equity, we lose 80k in closing costs, plus another 45k to simulate a 5% drop in value against inflation
                    capGainsTaxRate = 0.15
                    saleValue = (oldestRentalEquity - 80000 - 45000) * (1 - capGainsTaxRate)
                    if saleValue > 0:
                        rentalHomes.pop(oldestRentalID)
                        savings += saleValue
                        # lowSavings = savings
                        sellRentals = False  # only do this once
            if lowSavings < 0:
                otherIncome = int(otherIncome)
                savings = int(savings)
                equity = int(equity)
                break

        if foreverHome:
            savings = savings * (1 + (savingsReturnRate / 12))

        printAnnualStats = False
        if i % 12 == 0:
            age += 1
            otherIncome = int(otherIncome)
            savings = int(savings)
            equity = int(equity)
            printRetiredAge = retireAge if retireAge else (39 + (retireMonth / 12))
            netSavings = currentMonthlySavings + otherIncome
            if printAnnualStats and netSavings > 0 and retired:
                print(
                    "For age:",
                    age,
                    "| year is:",
                    year,
                    "| retireAge is:",
                    printRetiredAge,
                    "| rentals paid off:",
                    numRentalsPaidOff,
                    "| netSavings is:",
                    "${:,.2f}".format(netSavings),
                    "| pensionIncome is:",
                    "${:,.2f}".format(pensionIncome),
                    "| currentMonthlySavings is:",
                    "${:,.2f}".format(currentMonthlySavings),
                    "| savings is:",
                    "${:,.2f}".format(savings),
                    "| lowSavings is:",
                    "${:,.2f}".format(lowSavings),
                    "| currentMonthlyBudget is:",
                    "${:,.2f}".format(currentMonthlyBudget),
                    "| equity is:",
                    "${:,.2f}".format(equity),
                )
        printForeverHomeTracking = False
        if printForeverHomeTracking:
            # if not foreverHome:
            if i < 100:
                otherIncome = int(otherIncome)
                savings = int(savings)
                equity = int(equity)
                printRetiredAge = retireAge if retireAge else (39 + (retireMonth / 12))
                print(
                    "For ",
                    monthName + " " + str(year),
                    "| currentMonthlySavings is:",
                    "${:,.2f}".format(currentMonthlySavings),
                    "| savings is:",
                    "${:,.2f}".format(savings),
                    "| otherIncome is:",
                    "${:,.2f}".format(otherIncome),
                    "| currentMonthlyBudget is:",
                    "${:,.2f}".format(currentMonthlyBudget),
                )

    return (
        age,
        int(currentMonthlySavings),
        int(otherIncome),
        int(lowSavings),
        int(savings),
        int(equity),
        foreverHomeDate,
        int(incomeAt75),
        int(incomeAt85),
        int(budgetAt85),
        int(savingsAt75),
        int(savingsAt85),
        int(equityAt75),
        int(equityAt85),
        int(numRentalsPaidOff),
        rentalHomes,
    )


def planRetirement(event, context):
    # economy
    inflation = event.get("inflation", 0.0313)
    returnRate = event.get("returnRate", 0.05)
    postRetirementReturnRate = event.get("postRetirementReturnRate", 0.0313)
    # budgets
    monthlyBudget = event.get("monthlyBudget", 5500)
    oopsBudget = event.get("oopsBudget", 0)
    travelBudget = event.get("travelBudget", 1000)
    retirementReduction = event.get("retirementReduction", 0.25)
    early40sReduction = event.get("early40sReduction", 0.05)
    maxRentals = int(event.get("maxRentals", 3))
    foreverHomeCost = int(event.get("foreverHomeCost", 750000))
    extraHollandMonths = int(event.get("extraHollandMonths", 0))

    # # economy
    # inflation = event["inflation"]
    # returnRate = event["returnRate"]
    # postRetirementReturnRate = event["postRetirementReturnRate"]
    # # budgets
    # monthlyBudget = event["monthlyBudget"]
    # oopsBudget = event["oopsBudget"]
    # travelBudget = event["travelBudget"]
    # retirementReduction = event["retirementReduction"]
    # early40sReduction = event["early40sReduction"]
    # maxRentals = int(event["maxRentals"])
    # foreverHomeCost = event["foreverHomeCost"]

    foreverHomeMortgage = foreverHomeCost * 0.00595

    # income calculation
    jimNetWages = calculateNetWages(
        grossMonthly, healthDeduction, jim401kContribution, taxes, lifeDeduction, fersDeduction
    )

    hollandSavingsPrePPS = (
        jimNetWages
        + total401kContribution
        + carleyPrePPSsavings
        - (monthlyBudget * (1 - early40sReduction))
        - travelBudget
        - oopsBudget
        - hollandMortgage
        - hollandUtilites
    )

    # print("jimNetWages: ", jimNetWages)
    # print("total401kContribution: ", total401kContribution)
    # print("carleyPrePPSsavings: ", carleyPrePPSsavings)
    # print("monthlyBudget: ", monthlyBudget)
    # print("travelBudget: ", travelBudget)
    # print("oopsBudget: ", oopsBudget)
    # print("hollandMortgage: ", hollandMortgage)
    # print("hollandUtilites: ", hollandUtilites)

    # print("hollandSavingsPrePPS before student and car loan: ", hollandSavingsPrePPS)

    hollandSavingsPPS = (
        jimNetWages
        + total401kContribution
        + carleyPPSsavings
        - monthlyBudget
        - travelBudget
        - oopsBudget
        - hollandMortgage
        - hollandUtilites
    )

    # print("hollandSavingsPPS before student and car loan: ", hollandSavingsPPS)

    foreverHomeSavings = (
        jimNetWages
        + carleyPPSsavings
        + total401kContribution
        - monthlyBudget
        - travelBudget
        - oopsBudget
        - foreverHomeMortgage
        - foreverHomeUtilities
    )

    # print("foreverHomeSavings before student and car loan: ", foreverHomeSavings)

    monthsToLive = (60 * 12) + 6  # month 1 is June, 2022
    months = monthsToLive
    age = 39
    retireMonth = 120
    retireAge = age + (retireMonth / 12)
    maxRetireMonth = 36 * 12
    maxRetireAge = 75
    lowSavingsTest = -9999999999
    months = monthsToLive
    # while lowSavingsTest < 24999 and retireAge < maxRetireAge:
    while lowSavingsTest < 24999 and retireMonth < maxRetireMonth:

        retireAge = 0
        # retireAge += 1
        retireMonth += 1
        (
            ageTest,
            monthlySavingsTest,
            otherIncomeTest,
            lowSavingsTest,
            savingsTest,
            equityTest,
            foreverHomeDateTest,
            incomeAt75Test,
            incomeAt85Test,
            budgetAt85Test,
            savingsAt75Test,
            savingsAt85Test,
            equityAt75Test,
            equityAt85Test,
            numRentalsPaidOffTest,
            rentalHomesTest,
        ) = iterateMonthlyForecast(
            months,
            retireAge,
            retireMonth,
            startingSavings,
            monthlyBudget,
            hollandSavingsPrePPS,
            hollandSavingsPPS,
            foreverHomeSavings,
            maxRentals,
            travelBudget,
            oopsBudget,
            inflation,
            early40sReduction,
            retirementReduction,
            returnRate,
            postRetirementReturnRate,
            foreverHomeCost,
            extraHollandMonths,
            sellRentals=False,
        )
    retireAge = age + (retireMonth / 12)
    print(
        "For budget:",
        monthlyBudget,
        "| retirement age is:",
        "{:2f}".format(retireAge),
        "| maxRentals is:",
        maxRentals,
        "| foreverHomeDate is:",
        foreverHomeDateTest,
        "| lowSavings is:",
        "${:,.2f}".format(lowSavingsTest),
        "| rentals paid off is:",
        numRentalsPaidOffTest,
        "| incomeAt75 is:",
        "${:,.2f}".format(incomeAt75Test),
        "| incomeAt85 is:",
        "${:,.2f}".format(incomeAt85Test),
        "| savingsAt75 is:",
        "${:,.2f}".format(savingsAt75Test),
        "| savingsAt85 is:",
        "${:,.2f}".format(savingsAt85Test),
        "| equityAt75 is:",
        "${:,.2f}".format(equityAt75Test),
        "| equityAt85 is:",
        "${:,.2f}".format(equityAt85Test),
    )
    body = {
        "retireAge": retireAge,
        "monthlySavings": monthlySavingsTest,
        "otherIncome": otherIncomeTest,
        "lowSavings": lowSavingsTest,
        "savings": savingsTest,
        "equity": equityTest,
        "foreverHomeDate": foreverHomeDateTest,
        "incomeAt85": incomeAt85Test,
        "budgetAt85": budgetAt85Test,
        "savingsAt75": savingsAt75Test,
        "savingsAt85": savingsAt85Test,
        "equityAt75": equityAt75Test,
        "equityAt85": equityAt85Test,
        "numRentalsPaidOff": numRentalsPaidOffTest,
        "rentalHomes": rentalHomesTest,
    }
    return 200, body


def respond(err, code, body=None):
    function_response = {
        "statusCode": "400" if err else "200",
        "body": json.dumps({"error": err}) if err else json.dumps(body),
        "headers": {
            "Content-Type": "application/json",
        },
    }
    # log.info("Response: %s", function_response)
    print("Outgoing response body: ", function_response["body"])
    return function_response


def lambda_handler(event, context):
    err = None
    body = None
    status_code = 500
    try:
        try:
            postBody = json.loads(event["body"])
        except:
            postBody = event["body"]
        print("Incoming POST body: ", postBody)
        status_code, body = planRetirement(postBody, context)
        # body["postBody"] = postBody
        if status_code != 200:
            log.error(
                "Request to slack returned an error, status code %s, with text: %s",
                status_code,
                body,
            )
            err = body
        return respond(err, status_code, body)
    except Exception as err:
        print("Encountered error:", err, "with trace:", traceback.format_exc())
        return respond(str(err), status_code, body)


event = {
    "body": {
        "inflation": 0.0313,
        "returnRate": 0.055,
        "postRetirementReturnRate": 0.0313,
        "monthlyBudget": 4500,
        "oopsBudget": 250,
        "travelBudget": 1000,
        "retirementReduction": 0.25,
        "early40sReduction": 0.00,
        "maxRentals": 2,
        "foreverHomeCost": 750000,
        "extraHollandMonths": 0,
    }
}

print("######################################################")
print("~~~~~~~~~~~~~~~~~~~~~~~~ BODY ~~~~~~~~~~~~~~~~~~~~~~~~")
# print(event)
print("~~~~~~~~~~~~~~~~~~~~~~~ RESULT ~~~~~~~~~~~~~~~~~~~~~~~")
try:
    event["body"] = json.dumps(event["body"])
    lambda_handler(event, None)
    print("######################################################")
except Exception as err:
    print("Encountered error:", err, "with trace:", traceback.format_exc())
