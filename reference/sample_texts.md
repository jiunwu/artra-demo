# 範例分類學文本（用於測試與 Few-shot Prompt）

## Example 1: Single Species Description (Simple)

**Source style**: Morphological description from a taxonomic treatment

```
Pachybrachis sassii Daccordi & Busato, a new species from the Mediterranean Giglio Island (Italy) (Coleoptera, Chrysomelidae, Cryptocephalinae). Body length 3.2–3.8 mm. Body oval, moderately convex. Head black with brownish-yellow labrum. Antennae with 11 segments, basal four segments yellowish-brown, remaining segments dark brown. Pronotum black, shiny, finely and sparsely punctate. Elytra black with irregular yellowish spots, coarsely and densely punctate. Legs yellowish-brown with darker femora. This species is found in maquis shrubland habitats at elevations of 100–400 m.
```

**Expected extraction**:
```json
{
  "entities": [
    {"text": "Pachybrachis sassii", "type": "Arthropod", "start": 0, "end": 19},
    {"text": "Coleoptera", "type": "Arthropod", "start": 96, "end": 106},
    {"text": "Chrysomelidae", "type": "Arthropod", "start": 108, "end": 121},
    {"text": "Body length", "type": "Trait", "start": 140, "end": 151},
    {"text": "3.2–3.8 mm", "type": "Value", "start": 152, "end": 162},
    {"text": "Body oval, moderately convex", "type": "Value", "start": 164, "end": 192},
    {"text": "Head", "type": "Trait", "start": 194, "end": 198},
    {"text": "black with brownish-yellow labrum", "type": "Value", "start": 199, "end": 231},
    {"text": "Antennae", "type": "Trait", "start": 233, "end": 241},
    {"text": "11 segments", "type": "Value", "start": 247, "end": 258},
    {"text": "habitat", "type": "Trait", "start": 480, "end": 487},
    {"text": "maquis shrubland", "type": "Value", "start": 463, "end": 479},
    {"text": "elevations", "type": "Trait", "start": 500, "end": 510},
    {"text": "100–400 m", "type": "Value", "start": 514, "end": 523}
  ],
  "triplets": [
    {"arthropod": "Pachybrachis sassii", "trait": "body length", "value": "3.2–3.8 mm"},
    {"arthropod": "Pachybrachis sassii", "trait": "head color", "value": "black with brownish-yellow labrum"},
    {"arthropod": "Pachybrachis sassii", "trait": "antennae segments", "value": "11"},
    {"arthropod": "Pachybrachis sassii", "trait": "habitat", "value": "maquis shrubland"},
    {"arthropod": "Pachybrachis sassii", "trait": "elevation", "value": "100–400 m"}
  ]
}
```

---

## Example 2: Multi-Species Comparison (Medium)

**Source style**: Comparative description from a revisionary study

```
Three species of the genus Tipula (Diptera, Tipulidae) are compared from the New World. Tipula americana has a body length of 15.2–18.6 mm, wing length 16.0–19.5 mm, and is commonly found in deciduous forests of eastern North America at elevations of 200–1500 m. The species is a detritivore, feeding primarily on decaying leaf litter. Tipula mexicana is slightly smaller, with body length 12.8–15.1 mm and wing length 13.5–16.2 mm, inhabiting montane cloud forests in central Mexico at 1800–2800 m elevation. Tipula borealis is the largest species, with body length 19.0–22.3 mm, occurring in boreal forests and tundra of northern Canada. All three species have elongated legs with tibial spurs, characteristic of the family. The larvae are aquatic or semi-aquatic, developing in moist soil near streams.
```

**Expected extraction**:
```json
{
  "triplets": [
    {"arthropod": "Tipula americana", "trait": "body length", "value": "15.2–18.6 mm"},
    {"arthropod": "Tipula americana", "trait": "wing length", "value": "16.0–19.5 mm"},
    {"arthropod": "Tipula americana", "trait": "habitat", "value": "deciduous forests"},
    {"arthropod": "Tipula americana", "trait": "distribution", "value": "eastern North America"},
    {"arthropod": "Tipula americana", "trait": "elevation", "value": "200–1500 m"},
    {"arthropod": "Tipula americana", "trait": "feeding ecology", "value": "detritivore"},
    {"arthropod": "Tipula mexicana", "trait": "body length", "value": "12.8–15.1 mm"},
    {"arthropod": "Tipula mexicana", "trait": "wing length", "value": "13.5–16.2 mm"},
    {"arthropod": "Tipula mexicana", "trait": "habitat", "value": "montane cloud forests"},
    {"arthropod": "Tipula mexicana", "trait": "distribution", "value": "central Mexico"},
    {"arthropod": "Tipula mexicana", "trait": "elevation", "value": "1800–2800 m"},
    {"arthropod": "Tipula borealis", "trait": "body length", "value": "19.0–22.3 mm"},
    {"arthropod": "Tipula borealis", "trait": "habitat", "value": "boreal forests and tundra"},
    {"arthropod": "Tipula borealis", "trait": "distribution", "value": "northern Canada"},
    {"arthropod": "Tipulidae", "trait": "leg morphology", "value": "elongated with tibial spurs"},
    {"arthropod": "Tipula", "trait": "larval habitat", "value": "aquatic or semi-aquatic"}
  ]
}
```

---

## Example 3: Full Taxonomic Treatment (Complex)

**Source style**: Complete species description with diagnosis, distribution, and ecology

```
Order Hymenoptera, Family Formicidae

Camponotus gigas Latreille, 1802

Diagnosis. One of the largest ant species in Southeast Asia. Workers polymorphic, with major workers reaching body length of 28.0–30.5 mm and minor workers 18.0–22.0 mm. Head subquadrate in major workers, with prominent mandibles bearing 7–8 teeth. Mesosoma robust, propodeum rounded in profile. Gaster ovate, densely covered with fine pubescence. Overall coloration black, with reddish-brown tarsi and mandibles.

Distribution. Widely distributed across Peninsular Malaysia, Borneo, Sumatra, and Java. Found primarily in lowland and hill dipterocarp forests at elevations ranging from sea level to 1200 m. Colony density estimated at 0.5–1.2 colonies per hectare in primary forest.

Ecology. Camponotus gigas is predominantly nocturnal, foraging on tree trunks and canopy branches. The species is omnivorous, feeding on honeydew from hemipteran insects, plant exudates, and occasionally small arthropod prey. Nests are typically constructed in dead standing trees or large fallen logs, with colony sizes ranging from 5,000 to 8,000 workers. Foraging trails can extend up to 100 m from the nest entrance. Workers exhibit strong territorial behavior, engaging in ritualized combat with conspecific colonies at territory boundaries.

Remarks. This species was previously confused with C. pennsylvanicus from North America. The two species can be distinguished by the larger body size of C. gigas and differences in propodeal shape. Genetic analysis based on COI barcoding confirms their placement in separate species groups.
```

---

## Few-shot Prompt Examples（供 prompts.py 使用）

### Mini Example A（用於 prompt 內的 few-shot）
**Input**: `Aedes aegypti (Diptera, Culicidae) has a body length of 4–7 mm and is found in tropical urban areas worldwide. The species is a blood-feeding ectoparasite, primarily active during daytime.`

**Output**:
```json
{
  "entities": [
    {"text": "Aedes aegypti", "type": "Arthropod"},
    {"text": "Diptera", "type": "Arthropod"},
    {"text": "Culicidae", "type": "Arthropod"},
    {"text": "body length", "type": "Trait"},
    {"text": "4–7 mm", "type": "Value"},
    {"text": "habitat", "type": "Trait"},
    {"text": "tropical urban areas", "type": "Value"},
    {"text": "distribution", "type": "Trait"},
    {"text": "worldwide", "type": "Value"},
    {"text": "feeding ecology", "type": "Trait"},
    {"text": "blood-feeding ectoparasite", "type": "Value"},
    {"text": "activity pattern", "type": "Trait"},
    {"text": "daytime", "type": "Value"}
  ],
  "triplets": [
    {"arthropod": "Aedes aegypti", "trait": "body length", "value": "4–7 mm"},
    {"arthropod": "Aedes aegypti", "trait": "habitat", "value": "tropical urban areas"},
    {"arthropod": "Aedes aegypti", "trait": "distribution", "value": "worldwide"},
    {"arthropod": "Aedes aegypti", "trait": "feeding ecology", "value": "blood-feeding ectoparasite"},
    {"arthropod": "Aedes aegypti", "trait": "activity pattern", "value": "daytime"}
  ]
}
```

### Mini Example B（用於 prompt 內的 few-shot）
**Input**: `The spider Argiope bruennichi (Araneae, Araneidae) constructs orb webs in grassland habitats across Europe and Asia. Females have a body length of 15–25 mm with distinctive yellow and black banding on the abdomen. Males are significantly smaller at 4–6 mm.`

**Output**:
```json
{
  "entities": [
    {"text": "Argiope bruennichi", "type": "Arthropod"},
    {"text": "Araneae", "type": "Arthropod"},
    {"text": "Araneidae", "type": "Arthropod"},
    {"text": "web type", "type": "Trait"},
    {"text": "orb webs", "type": "Value"},
    {"text": "habitat", "type": "Trait"},
    {"text": "grassland", "type": "Value"},
    {"text": "distribution", "type": "Trait"},
    {"text": "Europe and Asia", "type": "Value"},
    {"text": "body length (female)", "type": "Trait"},
    {"text": "15–25 mm", "type": "Value"},
    {"text": "coloration", "type": "Trait"},
    {"text": "yellow and black banding on the abdomen", "type": "Value"},
    {"text": "body length (male)", "type": "Trait"},
    {"text": "4–6 mm", "type": "Value"}
  ],
  "triplets": [
    {"arthropod": "Argiope bruennichi", "trait": "web type", "value": "orb webs"},
    {"arthropod": "Argiope bruennichi", "trait": "habitat", "value": "grassland"},
    {"arthropod": "Argiope bruennichi", "trait": "distribution", "value": "Europe and Asia"},
    {"arthropod": "Argiope bruennichi", "trait": "body length (female)", "value": "15–25 mm"},
    {"arthropod": "Argiope bruennichi", "trait": "coloration", "value": "yellow and black banding on the abdomen"},
    {"arthropod": "Argiope bruennichi", "trait": "body length (male)", "value": "4–6 mm"}
  ]
}
```
