[out:json][timeout:30];
area["name:en"="Islands District"]->.outer;
(
  nwr["shop"~"mall"](area.outer);
);
out geom;
