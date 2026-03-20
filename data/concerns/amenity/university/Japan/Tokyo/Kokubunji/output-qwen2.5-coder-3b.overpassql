[out:json][timeout:30];
area["name:en"="Kokubunji"]->.outer;
(
  nwr["amenity"="university"](area.outer);
);
out geom;
