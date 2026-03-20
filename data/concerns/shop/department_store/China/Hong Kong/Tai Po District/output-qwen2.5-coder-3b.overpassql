[out:json][timeout:30];
area["name:zh"="大埔區"]->.outer;
(
  nwr["shop"~"department_store"](area.outer);
);
out geom;
