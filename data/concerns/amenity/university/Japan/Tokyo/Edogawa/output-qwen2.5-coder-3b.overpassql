[out:json][timeout:30];
area["name:en"="Edogawa"]->.outer;
(
  nwr["amenity"="university"](area.outer);
);
out geom;
