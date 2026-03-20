[out:json][timeout:30];
area["name:en"="Aoba Ward"]->.outer;
(
  nwr["amenity"="university"](area.outer);
);
out geom;
