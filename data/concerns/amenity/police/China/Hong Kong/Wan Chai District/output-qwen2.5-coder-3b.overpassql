[out:json][timeout:30];
area["name:en"="Wan Chai District"]->.outer;
(
  nwr["amenity"~"police"](area.outer);
);
out geom;
