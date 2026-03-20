[out:json][timeout:30];
area["name:en"="Shinagawa"]->.outer;
(
  nwr["amenity"="university"](area.outer);
);
out geom;
