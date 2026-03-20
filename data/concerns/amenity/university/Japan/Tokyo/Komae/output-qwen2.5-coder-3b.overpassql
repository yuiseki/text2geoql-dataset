[out:json][timeout:30];
area["name:en"="Komae"]->.outer;
(
  nwr["amenity"="university"](area.outer);
);
out geom;
