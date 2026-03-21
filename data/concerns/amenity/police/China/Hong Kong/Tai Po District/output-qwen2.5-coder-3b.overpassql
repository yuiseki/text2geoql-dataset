[out:json][timeout:30];
area["name:en"="Tai Po District"]->.outer;
(
  nwr["amenity"~"police"](area.outer);
);
out geom;
