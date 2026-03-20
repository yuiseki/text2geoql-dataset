[out:json][timeout:30];
area["name:zh"="沙田區"]->.outer;
(
  nwr["shop"~"clothes"](area.outer);
);
out geom;
