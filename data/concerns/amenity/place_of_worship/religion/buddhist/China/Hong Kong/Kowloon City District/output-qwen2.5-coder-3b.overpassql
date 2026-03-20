[out:json][timeout:30];
area["name:en"="Kowloon City District"]->.outer;
(
  nwr["building"~"temple"](area.outer);
);
out geom;
