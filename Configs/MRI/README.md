# MRI Configuration

_This version of game is inspired by my experience in the Preclinical MRI industry_

- **boons.json**: Configures helium boon/shortage and rare-earth shortage
- **config.json**: Configures the required components and optional upgrades for preclinical MRI system manufacture

## Required Components

These decisions are _required_ to start producing a system. Once the players have made all these choices they can start making sales.

### Magnet

_You need a magnet to have an MRI scanner and a few different technologies exist_

- 'Wet' Magnet: a traditional MRI magnet where the magnet is supercooled using liquid helium
- Cryogen Free Magnet: A magnet that only uses a cryocompressor (and a small, fixed amount of helium) 
- Permanent magnet: A magnet made from rare-earth metals

### Subject Table

_You need a way to get the subject into the scanner_

- Manual: positioning of the subject is manual
- Automatic: position of the subject is controlled by software and driven into the magnet

### Casing

_Are you going to make your scanners look pretty or aim more for the researcher market_

- Bare: no casing, looks like a piece of research equipment 
- Covers: fibre glass casing more like those seen on clinical scanners

### User Software

_You need software to run the scanner_

- Standard: not particularly pretty but gets the job done
- Pretty: hey, you hired someone with decent UX and UI skills!

### Field Strength

_Magnet production is difficult and you also may need to use different RF components at certain field strengths_

- 0.1 Tesla: useful for rock imaging used by the oil & gas industry
- 0.55 Tesla: a low field system; lower image quality but easier to make widely available
- 1.5 Tesla: the old standard for clinical imaging
- 3 Tesla: the standard for clinical imaging
- 4.7 Tesla: less common clinically but often used preclinically
- 7 Tesla: there are now some clinical scanners at this field strength. Commonly used for preclinical imaging

## Upgrades

These are optional extras that will take time and money to research but can increase the sale price and rate of your systems by offering extra functionality.

### Additional Functionality

_Extra options that can increase sales chance and revenue_

- PET: Add Positron Emission Tomography to allow functional metabolic imaging in addition to MRI
- Cryo Probes: increased sensitivity RF probes
- Large Animals: Increase the bore size to allow imaging of a wider range of animals
- Spectroscopy: Software and sequence improvements to allow MR Spectroscopy
- DWI/DTI: Sequence improvements to allow functional MRI (fMRI)
- Cardiac: Different coils and sequences to support cardiac imaging

### Multinuclear

_Offering a full suite of multinuclear options increases chance of sale_

- 13C: Functional metabolic imaging
- 129Xe: Used for lung imaging and hyperpolarised MRI
- 19F: Quantitative imaging using perflurocarbons
- 23Na: Used for neuro imaging and spectroscopy 

## Boons & Shortages

These are events the games master can apply temporarily to simulate the changing prices of important resources.

### Helium

- the helium boon increases the revenue from wet magnets
- the helium shortage decreases the revenue from wet magnets

### Rare-Earth Metals

- the rare-earth shortage decreases the revenue from permanent magnets13c 