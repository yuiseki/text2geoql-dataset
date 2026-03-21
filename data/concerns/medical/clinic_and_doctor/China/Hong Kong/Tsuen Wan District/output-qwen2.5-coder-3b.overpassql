[out:json][timeout:30];
area["name:en"="Tsuen Wan District"]->.outer;
(
  nwr["amenity"~"clinic|doctor"](area.outer);
);
out geom;
