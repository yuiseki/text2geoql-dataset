[out:json][timeout:30];
area["name:en"="Wan Chai District"]->.outer;
(
  nwr["amenity"~"clinic|doctor"](area.outer);
);
out geom;
