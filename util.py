# Error messages:
memberError = "Name not found in database, please choose your name from the list of names available."
itemError = "Item not found in database, please choose from the list of items available."

startDateHistoricError = "A tervezett kölcsönzés kezdetének napja nem lehet korábban a mai napnál."
startDateInterruptError = "A tervezett kölcsönzés kezdetének napja egy másik kölcsönzés idejére esik."
borrowPeriodsMatchError = "A tervezett kölcsönzés időtartama megegyezik egy másik kölcsönzés időtartamával."
planDateEarlierError = "A kölcsönzés tervezett vége nem lehet korábban mint a kölcsönzés kezdete."
borrowsOverlapError = "A tervezett kölcsönzési időszakban egy másik kölcsönzés már elindul."

startDateOverlapAlert = "A tervezett kölcsönzés kezdetének napja egy másik kölcsönzés végének napjára esik. Kérlek egyeztess a másik kölcsönzővel. (A kölcsönzés rögzítésre került)"
planDateOverlapAlert = "A tervezett visszahozatali dátumon indul egy kölcsönzés. Kérlek egyeztess a másik kölcsönzővel. (A kölcsönzést rögzítésre került)"

startDateError = "Start date cannot be an earlier date than today."
planDateError = """Tervezett visszahozatali dátumnál hiba merült fel. Lehetséges okok: Korábbi dátum mint a kölcsönzés kezdete dátum,
                    kölcsönzés beleesik egy másik kölcsönzés időpontjába."""
successMessage = "Borrow successfully registered!"
errorMessage = "Something went wrong."
