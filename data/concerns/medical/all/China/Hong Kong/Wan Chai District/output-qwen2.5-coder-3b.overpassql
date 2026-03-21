[out:json][timeout:30];
area["name:en"="Wan Chai District"]->.outer;
(
  nwr["amenity"~"hospital|clinic"](area.outer);
);
out geom;
