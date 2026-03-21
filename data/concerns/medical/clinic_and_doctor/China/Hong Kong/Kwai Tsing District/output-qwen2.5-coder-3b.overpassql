[out:json][timeout:30];
area["name:en"="Kwai Tsing District"]->.outer;
(
  nwr["amenity"~"clinic|doctor"](area.outer);
);
out geom;
