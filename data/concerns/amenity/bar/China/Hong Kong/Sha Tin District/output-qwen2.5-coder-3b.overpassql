[out:json][timeout:30];
area["name:en"="Sha Tin District"]->.outer;
(
  nwr["amenity"~"bar"](area.outer);
);
out geom;
