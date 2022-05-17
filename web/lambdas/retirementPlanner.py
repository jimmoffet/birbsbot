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
startingSavings = 70000
# real estate
hollandMortage = 600
hollandUtilites = 400
# foreverHomeMortgage = 4200
foreverHomeUtilities = 500
vacancyRate = 0.04
propManRate = 0.09  # includes half month for new tenants
lombardHollandNetIncome = (
    325  # includes 100/mo HELOC pmt, but not 450 fedloan payment (currently coming from oops budget)
)
lombardHollandEquity = 250000
rentalIncomeNominal = 120000  # let's take 10% of the top as a cushion
# income
grossMonthly = 14167
healthDeduction = 600
jim401kContribution = 2292
employerContributionRate = 0.05
carleyPPSwagesBegin = 2025
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
pensionStartAge = 62
lifeDeduction = 50
disabilityDeduction = 20
employer401kcontribution = grossMonthly * employerContributionRate
total401kContribution = jim401kContribution + employer401kcontribution
carleyPrePPSsavings = 850
carleyPPSsavings = 2800
# taxes
fed = 0.1610
med = 0.0160
oasd = 0.0620
state = 0.0800
orTransit = 0.0010
orWorkerComp = 0.0002
taxes = [fed, med, oasd, state, orTransit, orWorkerComp]
# explicit safety margins
rentalIncomeSafetyMargin = 0.1


def calculateNetWages(grossMonthly, healthDeduction, monthly401k, taxes, lifeDeduction, disabilityDeduction):
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
    postTaxDeductions = healthDeduction + lifeDeduction + disabilityDeduction
    netWages = postTaxWages - postTaxDeductions
    return netWages


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
    lombardHollandNetIncome = (
        1000 * 0.66
    )  # 8000/yr after paying student loans and home imp and holland mortgage reduction? Doubtful... This probably consumes the entire oops budget...
    lombardHollandEquity = 250000
    monthlySavings = hollandSavingsPrePPS
    currentMonthlyBudget = monthlyBudget
    currentMonthlySavings = monthlySavings

    # extraHollandMonths = 3
    foreverHomeDelayedMonth = -1

    age = 39

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

    for i in range(1, months):
        if i % 12 == 7:
            year += 1
        monthName = calendar.month_name[((i + 5) % 12) + 1]

        if i == 30:  # assume it takes C 6 months to start earning 53k
            monthlySavings = hollandSavingsPPS
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
        else:
            currentMonthlyBudget = monthlyBudget

        if age >= pensionStartAge:
            minAge = math.trunc(age) if age <= 67 else 67
            pensionIncome = monthlyPensionDict[minAge][0]
            # pensionIncome = monthlyPensionNet
        else:
            pensionIncome = 0

        if foreverHome and (i - foreverHomePurchaseMonth) == 360:
            foreverHomeMortgage = foreverHomeMortgage * 0.32

        if not retireAge:
            if i >= retireMonth:
                retired = True
                retirementDate = monthName + " " + str(year)
                currentMonthlyBudget = monthlyBudget * (1 - retirementReduction)
                currentMonthlySavings = (
                    pensionIncome
                    - currentMonthlyBudget
                    - travelBudget
                    - oopsBudget
                    - foreverHomeMortgage
                    - foreverHomeUtilities
                )
            if age == 70:
                oopsBudget = 250
                travelBudget = 250
        else:
            if age >= retireAge:
                retired = True
                currentMonthlyBudget = monthlyBudget * (1 - retirementReduction)
                if age == 70:
                    oopsBudget = 250
                    travelBudget = 250
                currentMonthlySavings = (
                    pensionIncome
                    - currentMonthlyBudget
                    - travelBudget
                    - oopsBudget
                    - foreverHomeMortgage
                    - foreverHomeUtilities
                )

        savings = savings + currentMonthlySavings + otherIncome

        if savings > ((foreverHomeCost * 0.2) + foreverHomeReno + foreverHomePurchaseMinReserve) and not foreverHome:
            if foreverHomeDelayedMonth == -1:
                foreverHomeDelayedMonth = i + extraHollandMonths
            if i == foreverHomeDelayedMonth:
                foreverHome = True
                savings = savings - ((foreverHomeCost * 0.2) + foreverHomeReno)
                foreverHomeEquity = (foreverHomeCost * 0.2) + foreverHomeReno
                foreverHomePurchaseMonth = i
                monthlySavings = foreverHomeSavings
                currentMonthlySavings = monthlySavings
                # print("Bought forever home in ", monthName, "", year)
                foreverHomeDate = monthName + " " + str(year)

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
                        lowSavings = savings
                        sellRentals = False  # only do this once
            if lowSavings < 0:
                otherIncome = int(otherIncome)
                savings = int(savings)
                equity = int(equity)
                break

        if 12 < i < 30:
            savings = savings - carleyPrePPSsavings  # Carley not working during gtep
        if foreverHome:
            savings = savings * (1 + (savingsReturnRate / 12))
        if i % 12 == 0:
            age += 1
            otherIncome = int(otherIncome)
            savings = int(savings)
            equity = int(equity)
            printRetiredAge = retireAge if retireAge else (39 + (retireMonth / 12))
            # print(
            #     "For age:",
            #     age,
            #     "| year is:",
            #     year,
            #     "| retireAge is:",
            #     printRetiredAge,
            #     "| rentals paid off:",
            #     numRentalsPaidOff,
            #     "| currentMonthlySavings is:",
            #     "${:,.2f}".format(currentMonthlySavings),
            #     "| savings is:",
            #     "${:,.2f}".format(savings),
            #     "| lowSavings is:",
            #     "${:,.2f}".format(lowSavings),
            #     "| currentMonthlyBudget is:",
            #     "${:,.2f}".format(currentMonthlyBudget),
            #     "| equity is:",
            #     "${:,.2f}".format(equity),
            # )

    return (
        age,
        int(currentMonthlySavings),
        int(otherIncome),
        int(lowSavings),
        int(savings),
        int(equity),
        foreverHomeDate,
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
    oopsBudget = event.get("oopsBudget", 1000)
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

    foreverHomeMortgage = foreverHomeCost * 0.0056

    # income calculation
    jimNetWages = calculateNetWages(
        grossMonthly, healthDeduction, jim401kContribution, taxes, lifeDeduction, disabilityDeduction
    )

    hollandSavingsPrePPS = (
        jimNetWages
        + total401kContribution
        + carleyPrePPSsavings
        - (monthlyBudget * (1 - early40sReduction))
        - travelBudget
        - oopsBudget
        - hollandMortage
        - hollandUtilites
    )

    hollandSavingsPPS = (
        jimNetWages
        + total401kContribution
        + carleyPPSsavings
        - monthlyBudget
        - travelBudget
        - oopsBudget
        - hollandMortage
        - hollandUtilites
    )

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
            sellRentals=True,
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
    log.info("Response: %s", function_response)
    print(function_response["body"])
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
        "monthlyBudget": 5500,
        "oopsBudget": 1000,
        "travelBudget": 1000,
        "retirementReduction": 0.00,
        "early40sReduction": 0.00,
        "maxRentals": 2,
        "foreverHomeCost": 750000,
        "extraHollandMonths": 0,
    }
}
### NOTE as buffer have removed carley pre-PPS income
print("######################################################")
print("~~~~~~~~~~~~~~~~~~~~~~~~ BODY ~~~~~~~~~~~~~~~~~~~~~~~~")
print(event)
print("~~~~~~~~~~~~~~~~~~~~~~~ RESULT ~~~~~~~~~~~~~~~~~~~~~~~")
try:
    event["body"] = json.dumps(event["body"])
    lambda_handler(event, None)
    print("######################################################")
except Exception as err:
    print("Encountered error:", err, "with trace:", traceback.format_exc())
