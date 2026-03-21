[out:json][timeout:30];
area["name:en"="Tuen Mun District"]->.outer;
(
  nwr["amenity"~"pharmacy"](area.outer);
);
out geom;
