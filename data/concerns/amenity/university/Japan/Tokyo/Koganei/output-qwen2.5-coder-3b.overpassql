[out:json][timeout:30];
area["name:en"="Koganei"]->.outer;
(
  nwr["amenity"="university"](area.outer);
);
out geom;
