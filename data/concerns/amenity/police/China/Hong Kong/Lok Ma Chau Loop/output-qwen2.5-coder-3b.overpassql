[out:json][timeout:30];
area["name:en"="Hong Kong"]->.outer;
(
  nwr["amenity"~"police"](area.outer);
);
out geom;
