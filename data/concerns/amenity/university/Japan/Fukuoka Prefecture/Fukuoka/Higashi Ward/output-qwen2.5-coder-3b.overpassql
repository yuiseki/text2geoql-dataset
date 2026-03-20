[out:json][timeout:30];
area["name:en"="Higashi Ward"]->.outer;
(
  nwr["amenity"="university"](area.outer);
);
out geom;
