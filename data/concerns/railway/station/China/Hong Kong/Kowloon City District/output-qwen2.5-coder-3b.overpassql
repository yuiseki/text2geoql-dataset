[out:json][timeout:30];
area["name:en"="Kowloon City District"]->.outer;
(
  nwr["railway"~"station"](area.outer);
);
out geom;
