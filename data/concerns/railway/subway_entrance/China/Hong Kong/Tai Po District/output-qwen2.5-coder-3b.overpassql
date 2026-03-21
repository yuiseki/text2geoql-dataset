[out:json][timeout:30];
area["name:en"="Tai Po District"]->.outer;
(
  nwr["railway"~"subway"](area.outer);
);
out geom;
