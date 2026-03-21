[out:json][timeout:30];
area["name:en"="Yuen Long District"]->.outer;
(
  nwr["amenity"~"police"](area.outer);
);
out geom;
