[out:json][timeout:30];
area["name:en"="Central and Western District"]->.outer;
(
  nwr["historic"~"ruins"](area.outer);
);
out geom;
