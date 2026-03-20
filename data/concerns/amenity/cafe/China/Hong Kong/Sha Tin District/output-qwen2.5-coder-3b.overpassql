[out:json][timeout:30];
area["name:en"="Sha Tin District"]->.outer;
(
  nwr["amenity"~"cafe"](area.outer);
);
out geom;
