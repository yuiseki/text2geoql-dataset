[out:json][timeout:30];
area["name:en"="Abeno Ward"]->.outer;
(
  nwr["amenity"="university"](area.outer);
);
out geom;
