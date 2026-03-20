[out:json][timeout:30];
area["name:en"="Tai Po District"]->.outer;
(
  nwr["amenity"~"cafe"](area.outer);
);
out geom;
