[out:json][timeout:30];
area["name:en"="Islands District"]->.outer;
(
  nwr["shop"~"clothes"](area.outer);
);
out geom;
