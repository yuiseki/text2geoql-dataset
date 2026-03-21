[out:json][timeout:30];
area["name:en"="Yuen Long District"]->.outer;
(
  nwr["leisure"~"bird_hide"](area.outer);
);
out geom;
