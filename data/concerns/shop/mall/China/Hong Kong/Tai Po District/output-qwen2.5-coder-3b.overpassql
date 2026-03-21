[out:json][timeout:30];
area["name:en"="Tai Po District"]->.outer;
(
  nwr["shop"~"mall"](area.outer);
);
out geom;
