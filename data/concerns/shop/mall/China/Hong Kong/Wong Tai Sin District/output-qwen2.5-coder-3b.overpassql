[out:json][timeout:30];
area["name:en"="Wong Tai Sin District"]->.outer;
(
  nwr["shop"~"mall"](area.outer);
);
out geom;
