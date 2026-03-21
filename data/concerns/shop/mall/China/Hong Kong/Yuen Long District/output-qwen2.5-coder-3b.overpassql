[out:json][timeout:30];
area["name:en"="Yuen Long District"]->.outer;
(
  nwr["shop"~"mall"](area.outer);
);
out geom;
