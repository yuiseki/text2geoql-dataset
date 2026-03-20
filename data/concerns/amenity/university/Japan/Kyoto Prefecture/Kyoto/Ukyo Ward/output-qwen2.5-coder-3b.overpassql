[out:json][timeout:30];
area["name:en"="Kyoto"]->.outer;
(
  nwr["amenity"="university"](area.outer);
);
out geom;
