# Indian accounting notes

Why a generic screen misreads an Indian listing.

## Promoter pledge

A promoter borrows against his own shareholding. The lender holds the shares as collateral with a margin trigger. When the price falls the lender sells; the selling pushes the price down further; the fall triggers more margin calls. The mechanism is reflexive, which is why it produces permanent losses rather than drawdowns.

There is no US analogue, because US public companies rarely have a controlling family whose personal borrowing is secured on the float.

**What to read:** the quarterly shareholding pattern on the NSE or BSE site discloses pledge as a percentage *of promoter holding*, not of total equity.

**Why the trend beats the level:** a stable 15% pledge on a cash-generative business is often survivable. A pledge moving 0% → 2% → 9% over three quarters is a promoter running out of other options. This engine vetoes on any increase.

## Related-party transactions

The standard route by which cash leaves a listed entity for a promoter-owned unlisted one: inflated purchases from a related supplier, loans and advances that are never repaid, royalty or brand-licence fees paid upward.

**What to read:** the related-party disclosure note (Ind AS 24). Look at loans and advances to related parties specifically, not just trading transactions — a trading relationship can be commercial; an unsecured advance to a promoter entity generally is not.

## Contingent liabilities

Disclosed in the notes, not on the balance sheet: disputed tax demands, guarantees given for subsidiaries and associates, claims not acknowledged as debt, letters of credit.

In Indian infrastructure, capital-goods and EPC names these routinely exceed net worth. A guarantee given for a struggling subsidiary is a liability in everything but presentation.

**Band used here:** under 25% of net worth is unremarkable; over 50% is a red flag. Disputed tax demands deserve less weight than guarantees given, because the former often sit in appeal for a decade.

## Auditor signals

In India, a mid-cycle auditor resignation is very often the last public signal before a collapse. The resignation letter itself is filed with the exchange and is worth reading — the language of "unable to obtain sufficient appropriate audit evidence" is doing specific work.

A qualified opinion, an emphasis of matter, or a CARO adverse remark all belong in the register. So does a change of auditor that is not a mandated rotation.

## Ind AS quirks that distort ratios

- **Ind AS 116 (leases)** moved operating leases onto the balance sheet as a right-of-use asset and a lease liability. This inflates total assets and reported debt for retail, aviation and logistics companies, depressing asset turnover and raising leverage against pre-2019 history. Comparisons across the transition are not like-for-like.
- **Ind AS 115 (revenue)** changed recognition timing for EPC and real-estate companies from percentage-of-completion in a way that makes revenue growth across the transition year unreliable.
- **Other income** in Indian statements often bundles treasury income, forex gains and one-off asset sales. A company with 30% of PBT from other income is not earning it from operations. This engine flags above 15%.
- **Effective tax rate** far below the ~25.17% statutory rate (s.115BAA plus surcharge and cess) usually means SEZ benefits, accumulated losses or deferred-tax writebacks — all of which lapse. Treat the resulting EPS as lower quality.

## Why banks and NBFCs are refused

Beneish and Altman are suppressed when `is_financial` is true, and this is deliberate.

For a bank, deposits are the liability and loans are the asset. Working capital is not a meaningful concept, so Altman's X1 is noise. Cash conversion cycle, EV/EBITDA and inventory turns are all undefined. Beneish's receivables and gross-margin terms have no equivalent.

The correct substitutions are GNPA and NNPA for asset quality, PCR for provisioning adequacy, CAR against the RBI minimum, NIM for spread, CASA for funding quality, and slippage ratio for the direction of stress. Those belong in a dedicated BFSI register — see `CONTRIBUTING.md`, it is the most wanted contribution to this repository.
