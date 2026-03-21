[out:json][timeout:30];
area["name:en"="Islands District"]->.outer;
(
  nwr["amenity"~"clinic|doctor"](area.outer);
);
out geom;
