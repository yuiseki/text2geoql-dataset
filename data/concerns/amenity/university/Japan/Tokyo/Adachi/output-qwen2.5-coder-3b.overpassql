[out:json][timeout:30];
area["name:en"="Adachi"]->.outer;
(
  nwr["amenity"="university"](area.outer);
);
out geom;
