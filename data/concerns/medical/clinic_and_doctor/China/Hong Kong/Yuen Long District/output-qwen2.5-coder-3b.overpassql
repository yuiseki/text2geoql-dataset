[out:json][timeout:30];
area["name:en"="Yuen Long District"]->.outer;
(
  nwr["amenity"~"clinic|doctor"](area.outer);
);
out geom;
